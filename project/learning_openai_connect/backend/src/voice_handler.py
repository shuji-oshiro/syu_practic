# backend/voice_handler.py

import os
import whisper
from openai import OpenAI
from dotenv import load_dotenv
from src.reg_menu_order import fuzzy_menu_match


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API経由でのwhisperを使用した音声テキスト認識
def transcribe_audio_file_on_APImodel(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    orders = fuzzy_menu_match(transcript.text)

    orders = "メニューは存在しません。"
    if len(orders)>0:
        orders = sorted(orders, key=lambda x: x[1], reverse=True)
        retunValue = orders[0]

    return retunValue



# impotしたwhisperを使用した音声テキスト認識　-> select model:small, medium, large
def transcribe_audio_file_on_localmodel(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        # oss whisper 
        model = whisper.load_model("base") 
        result = model.transcribe(file_path, language="ja")

    match_orders = fuzzy_menu_match(result["text"])

    retunValue = "メニューは存在しません。"
    
    print("retrun:",match_orders)
    if len(match_orders)>0:
        match_orders = sorted(match_orders, key=lambda x: x[1], reverse=True)
        retunValue = match_orders[0]

    return retunValue
 
