import io
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import subprocess
import sounddevice as sd
from scipy.io.wavfile import write
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def record_wav(filename="test_sample.wav", duration=3, fs=16000):
    
    
    print("録音開始（話してください）...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print("録音終了:", filename)

def convert_wav_to_webm(wav_path, webm_path):
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-c:a", "libopus", "-b:a", "32k", webm_path
    ]
    subprocess.run(cmd, check=True)
    print("変換完了:", webm_path)

def test_voice_recognition_success():
    wav_file = "test_sample.wav"
    webm_file = "test_sample.webm"

    try:
        # 録音前に一時停止
        print("録音準備ができたらEnterキーを押してください...")
        input()
        print("録音開始（3秒間話してください）...")
        record_wav(wav_file, duration=3)
        convert_wav_to_webm(wav_file, webm_file)

        # WebMファイルをPOST
        with open(webm_file, "rb") as f:
            files = {"file": ("test_sample.webm", f, "audio/webm")}
            response = client.post("/voice/", files=files)

        data = response.json()      
        if response.status_code != 200:
            print("エラー:", response.status_code, data)
            return
        print("音声認識結果:", data.get("reco_text", ""))
        match_menus = data.get("match_menus", [])
        if match_menus:
            print("マッチしたメニュー:")
            for menu in match_menus:
                menu_obj = json.loads(json.dumps(menu["menu"], ensure_ascii=False))
                print("-", menu_obj["name"], "(スコア:", menu["score"], ")")
        else:
            print("マッチしたメニューはありません。")

    finally:
        if os.path.exists(wav_file):
            os.remove(wav_file)
        if os.path.exists(webm_file):
            os.remove(webm_file)

if __name__ == "__main__":
    test_voice_recognition_success()
    print("テストが完了しました。")