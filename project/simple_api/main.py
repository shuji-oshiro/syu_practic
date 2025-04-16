from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# .env読み込み
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# 受け取るデータの定義（例：ユーザー名と年齢）
class UserData(BaseModel):
    name: str
    age: int

# POSTエンドポイント
@app.post("/process/")
async def process_data(data: UserData, request: Request):
    print("Headers:", request.headers)
    print("Body:", data)
    client_api_key = request.headers.get("X-API-KEY")

    # APIキーが一致しない場合は拒否
    if client_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 受け取ったデータを加工して返す
    message = f"{data.name}さんは、{data.age * 12}ヶ月生きてますね！"
    return {"message": message}





from starlette.middleware.base import BaseHTTPMiddleware
import logging

logging.basicConfig(level=logging.INFO)

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logging.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        return response

app.add_middleware(LogMiddleware)