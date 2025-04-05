# ブラウザで http://localhost:8000/github/ にアクセス
# GitHubのユーザー情報を取得して表示するFastAPIアプリケーション
# FastAPIを使ったGitHubのユーザー情報を取得して表示するサンプルコード
# uvicorn main:app --reload
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
url = os.getenv("APT_URL")

app = FastAPI()

class UserData(BaseModel):
    login: str
    public_repos: int

@app.post("/github/")
async def receive_github_data(data: UserData, request: Request):
    if request.headers.get("X-API-KEY") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {
        "message": f"{data.login}さんは、{data.public_repos} 個の公開リポジトリを持っています！"
    }
