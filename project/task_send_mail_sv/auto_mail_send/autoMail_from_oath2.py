# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 16:17:12 2025
Gmailを使った自動メール送信
OAuth2による認証

このスクリプトは、Google OAuth2認証を使用してGmail API経由でメールを送信する機能を提供します。
セキュリティを考慮し、アプリケーションパスワードではなくOAuth2認証を使用しています。

必要な準備:
1. Google Cloud Consoleでプロジェクトを作成
2. Gmail APIを有効化
3. OAuth2クライアントIDとシークレットを取得
4. client_secret.jsonをプロジェクトディレクトリに配置

@author: owner-pc
"""

import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth2 認証のスコープ（Gmail API）
# gmail.send: メール送信のみを許可するスコープ
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def read_task_list_json():
    """
    タスクリストをJSONファイルから読み込む関数
    
    Returns:
        list: タスクリスト(辞書型のリスト)
    """
    import json
    with open("tasks.json", "r", encoding="utf-8") as file:
        task_list = json.load(file)
    return task_list


def authenticate_gmail():
    """
    Gmail APIの認証を行い、認証情報を返す関数
    
    Returns:
        Credentials: 有効な認証情報オブジェクト
        
    処理の流れ:
    1. 既存のトークンファイルを確認
    2. トークンが無効な場合は新規認証を実行
    3. 認証情報をトークンファイルに保存
    """
    creds = None
    token_path = "token.json"

    # 以前のトークンがあればロード
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES) 

    # 認証が必要なら OAuth フローを実行
    if not creds or not creds.valid:
        # client_secret.jsonから認証情報を読み込み
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        # ローカルサーバーで認証を実行
        creds = flow.run_local_server(port=0)
        # 認証情報をトークンファイルに保存
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def send_email():
    """
    Gmail APIを使用してメールを送信する関数
    
    処理の流れ:
    1. Gmail APIの認証
    2. メールメッセージの作成
    3. Base64エンコード
    4. メール送信の実行
    
    エラーハンドリング:
    - メール送信に失敗した場合はエラーメッセージを表示
    """

    task_list = read_task_list_json()
    print(task_list)

    # Gmail APIの認証情報を取得
    creds = authenticate_gmail()
    # Gmail APIサービスのインスタンスを作成
    service = build("gmail", "v1", credentials=creds)

    for task in task_list:
        body_val = (f"タスク名: {task['task']} 期限：{task['datetime']}")
        
        to_address = ""
        for user, email in task['users'].items():
            print(f"- {user}: {email}")
            to_address += email + ","
        

        # メールの基本情報を設定
        sender = "okiko5020@gmail.com"  # 送信元のメールアドレス
        to = to_address      # 送信先のメールアドレス
        subject = body_val
        body = "これはGmail APIを使ったPythonのメール送信テストです！ 有効期限{body_val}"

        # メールメッセージの作成
        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        # メッセージをBase64エンコード（Gmail APIの要件）
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        message_body = {"raw": raw_message}

        try:
            # メールの送信を実行
            service.users().messages().send(userId="me", body=message_body).execute()
            print("✅ メール送信成功！")
        except Exception as e:
            # エラーが発生した場合のエラーハンドリング
            print(f"❌ メール送信エラー: {e}")

    return


# メイン処理の実行
if __name__ == "__main__":
    send_email()
