# Google Drive APIを使ってファイルをダウンロードするサンプルコード
# FastAPIを使ったGoogle OAuth認証のサンプルコード  
# uvicorn g_login_getFile:app --reload
# ブラウザで http://localhost:8000/auth/login にアクセス
# Googleアカウントでログイン（OAuth）
# access_token を取得  
# Drive API を使ってファイル一覧を取得
# 任意のファイルをダウンロード(実行環境のディレクトリ直下に保存)
# Google Drive APIのスコープを追加
# https://www.googleapis.com/auth/drive.readonly

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
def login(): #scopeを変更
    # Google Drive APIのスコープを追加
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/drive.readonly",
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
    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }).json()

    access_token = token_res.get("access_token")

    # ✅ Driveファイル一覧を取得
    files_res = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"pageSize": 5, "fields": "files(id, name)"}
    ).json()

    print(files_res)
    files = files_res.get("files", [])

    if not files:
        return {"message": "ファイルが見つかりませんでした"}

    # ✅ 1つ目のファイルをダウンロード（バイナリ）
    file_id = files[0]["id"]
    file_name = files[0]["name"]
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    file_data = requests.get(download_url, headers={
        "Authorization": f"Bearer {access_token}"
    })

    # ✅ ローカルに保存（例: downloaded_{file_name}）
    with open(f"downloaded_{file_name}", "wb") as f:
        f.write(file_data.content)

    return {
        "message": f"{file_name} をダウンロードしました",
        "file_id": file_id,
        "file_name": file_name
    }
