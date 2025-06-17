from pydantic import BaseModel

class VoiceResult(BaseModel):
    reco_text: str
    match_text: str
