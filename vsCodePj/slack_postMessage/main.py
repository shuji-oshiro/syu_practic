from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/slack/events")
async def slack_event(request: Request):
    payload = await request.json()
    
    # 初期確認用
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # メッセージイベント受信
    if payload.get("type") == "event_callback":
        event = payload.get("event")
        if event["type"] == "message" and "bot_id" not in event:
            user = event["user"]
            text = event["text"]
            print(f"User {user} replied: {text}")
            # ここで任意の処理（DBに保存、通知返信など）

    return {"ok": True}

