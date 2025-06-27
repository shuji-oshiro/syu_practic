import os
import whisper
from openai import OpenAI
from dotenv import load_dotenv
from backend.app.service.fuzzy_matcher import fuzzy_menu_match

load_dotenv(dotenv_path="backend/.env")

# OpenAI APIクライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Whisperモデルのロード
# ローカルモデルを使用する場合は、whisper.load_model("base")を使用
model = whisper.load_model("base")

# ローカルモデルを使用して音声ファイルを文字起こしする関数
def transcribe_audiofile_on_localmodel(file_path: str):
    result = model.transcribe(file_path, language="ja")
    reco_text = result.get("text", "")
    
    if not isinstance(reco_text, str):
        raise TypeError("Whisper result['text'] is not a string")
    
    reco_text = reco_text.strip()
    return reco_text

# # OpenAI APIを使用して音声ファイルを文字起こしする関数
def transcribe_audiofile_on_APImodel(file_path: str):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    reco_text = transcript.text.strip()
    return reco_text

# 音声認識処理
def speechRecognition(file_path: str):
    
    # ローカルモデルを使用して音声ファイルを文字起こしする関数
    reco_text = transcribe_audiofile_on_localmodel(file_path)
    match_orders = fuzzy_menu_match(reco_text)
    if match_orders:
        # スコアが高い順にソート
        match_orders = sorted(match_orders, key=lambda x: x[1], reverse=True)

    return reco_text, match_orders

