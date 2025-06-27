import os
import whisper
from openai import OpenAI
from dotenv import load_dotenv
from backend.app.service.fuzzy_matcher import fuzzy_menu_match

load_dotenv(dotenv_path="backend/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

model = whisper.load_model("base")

def transcribe_audio_file_on_localmodel(file_path: str):
    result = model.transcribe(file_path, language="ja")

    reco_text = result.get("text", "")
    if not isinstance(reco_text, str):
        raise TypeError("Whisper result['text'] is not a string")
    
    reco_text = reco_text.strip()
    match_orders = fuzzy_menu_match(reco_text)
    if match_orders:
        # スコアが高い順にソート
        match_orders = sorted(match_orders, key=lambda x: x[1], reverse=True)

    return reco_text, match_orders

def transcribe_audio_file_on_APImodel(file_path: str):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    reco_text = transcript.text.strip()

    match_orders = fuzzy_menu_match(reco_text)
    match_text = None
    if match_orders:
        match_orders = sorted(match_orders, key=lambda x: x[1], reverse=True)
        match_text = match_orders[0][0]

    return {"reco_text": reco_text, "match_text": match_text}
