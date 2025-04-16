# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 16:17:12 2025
Gmailを使った自動メール送信
OAuth2による認証

@author: owner-pc
"""

import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# OAuth2 認証のスコープ（Gmail API）
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# 認証処理
def authenticate_gmail():
    creds = None
    token_path = "token.json"

    # 以前のトークンがあればロード
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # 認証が必要なら OAuth フローを実行
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

# Gmail API でメールを送信
def send_email():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    sender = "okiko5020@gmail.com"  # 送信元Gmailアドレス
    to = "syutv117@gmail.com"  # 送信先
    subject = "OAuth2 経由のメール送信テスト"
    body = "これはGmail APIを使ったPythonのメール送信テストです！"

    # メール作成
    message = MIMEText(body)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    message_body = {"raw": raw_message}

    try:
        service.users().messages().send(userId="me", body=message_body).execute()
        print("✅ メール送信成功！")
    except Exception as e:
        print(f"❌ メール送信エラー: {e}")

# 実行
send_email()
