import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.schemas.voice_schema import VoiceResult
from backend.app.service.voice_handler import speechRecognition

router = APIRouter()

@router.post("/", response_model=VoiceResult)
async def handle_voice(file: UploadFile = File(...)):
    temp_path = "temp.webm"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # 音声ファイルをローカルモデルで処理
        reco_text, match_menus = speechRecognition(temp_path)
        if len(match_menus) == 0:
            raise HTTPException(status_code=400, detail=f"音声認識エラー: {reco_text}")
    
        return {
            "reco_text": reco_text, 
            "match_menus": [
                {
                    "menu": menu,
                    "score": score
                } for menu, score in match_menus
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音声処理エラー: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
