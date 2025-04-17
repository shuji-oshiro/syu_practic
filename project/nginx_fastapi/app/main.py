# app/main.py
import logging
import sys

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/submit")
async def submit(name: str = Form(...)):
    logger.debug(f"フォーム送信: {name}")
    return JSONResponse(content={"msg": f"こんにちは、{name}さん！"})
