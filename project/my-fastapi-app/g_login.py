# FastAPIを使ったGoogle OAuth認証のサンプルコード
#  Step 1：Googleアカウントでログイン（OAuth認証）
#  Step 2：アクセストークンを取得
#  Step 3：GoogleのAPI（プロフィール情報やカレンダーなど）にアクセス
# .env にGoogleのクライアントID/シークレットを設定
# uvicorn g_login:app --reload
# ブラウザで http://localhost:8000/auth/login にアクセス
# Googleアカウントでログイン → ユーザー情報が表示される！
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import requests
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"

app = FastAPI()

@app.get("/")
def index():
    return {"message": "こんにちは！Googleでログインしてください /auth/login"}

@app.get("/auth/login")
def login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@app.get("/auth/callback")
def auth_callback(request: Request):
    code = request.query_params.get("code")

    # アクセストークンを取得
    token_req = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    })

    token_res = token_req.json()
    access_token = token_res.get("access_token")

    # ユーザー情報取得
    user_info_req = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={
        "Authorization": f"Bearer {access_token}"
    })

    user_info = user_info_req.json()
    return {
        "Googleから取得したユーザー情報": user_info
    }
