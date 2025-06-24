import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.schemas.voice_schema import VoiceResult
from backend.app.service.voice_handler import transcribe_audio_file_on_localmodel

router = APIRouter()

@router.post("/", response_model=VoiceResult)
async def handle_voice(file: UploadFile = File(...)):
    temp_path = "temp.webm"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # 音声ファイルをローカルモデルで処理
        result: VoiceResult
        result = VoiceResult.model_validate(transcribe_audio_file_on_localmodel(temp_path))
        
        if result.match_text is None:
            raise HTTPException(status_code=400, detail=f"音声処理エラー: メニューは存在しません。音声内容: {result.reco_text}")

        os.remove(temp_path)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音声処理エラー: {str(e)}")

