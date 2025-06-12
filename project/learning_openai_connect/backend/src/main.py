# backend/main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.voice_handler import transcribe_audio_file_on_localmodel 

load_dotenv()
app = FastAPI()

# CORS設定（Vue開発サーバと連携するため）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/voice")
async def handle_voice(file: UploadFile = File(...)):
    temp_path = "temp.webm"

    # 音声ファイルを保存
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    # Whisper APIでテキスト変換
    # text = transcribe_audio_file(temp_path)
    text = transcribe_audio_file_on_localmodel(temp_path)

    # 一時ファイル削除（必要に応じて）
    os.remove(temp_path)

    return {"text": text}
