# app/main.py
import logging
import sys
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import datetime
import pytz

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)

# タイムゾーンを日本時間に設定
logging.Formatter.converter = lambda *args: datetime.datetime.now(pytz.timezone('Asia/Tokyo')).timetuple()

logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/api/submit")
async def submit(name: str = Form(...)):
    logger.debug(f"フォーム送信: {name}")
    return JSONResponse(content={"msg": f"こんにちは、{name}さん！"})
