from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

app = FastAPI()

class UserData(BaseModel):
    login: str
    public_repos: int

@app.post("/github/")
async def receive_github_data(data: UserData, request: Request):
    if request.headers.get("X-API-KEY") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Slackに送るメッセージ
    slack_message = {
        "text": f"🐙 GitHubユーザー *{data.login}* さんは公開リポジトリを *{data.public_repos}* 個持っています！1234"
    }

    # Slack通知を送信
    slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)

    if slack_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Slack通知に失敗しました")

    return {
        "message": f"{data.login}さんの情報を受け取り、Slackに通知しました！"
    }

@app.post("/slack/events")
async def handle_slack_event(request: Request):
    payload = await request.json()
    print("Slack Event:", payload)
    return {"ok": True}
