# -*- coding: utf-8 -*-
# iCloud から写真をダウンロードするスクリプト
# 必要なライブラリをインストールする必要があります
# pip install pyicloud
import os
from pyicloud import PyiCloudService

# 環境変数から認証情報を読み込む例（推奨）
import os
APPLE_ID = os.getenv("APPLE_ID", "your_email@example.com")
APPLE_PASSWORD = os.getenv("APPLE_PASSWORD", "your_password")

# iCloud サービスにログイン
api = PyiCloudService(APPLE_ID, APPLE_PASSWORD)

# 2要素認証の処理（必要な場合）
if api.requires_2fa:
    print("2要素認証が必要です。")
    code = input("認証コードを入力してください: ")
    result = api.validate_2fa_code(code)
    if not result:
        print("2要素認証の検証に失敗しました。")
        exit(1)
    else:
        print("2要素認証に成功しました。")

# 保存先フォルダの設定
SAVE_DIR = "icloud_photos"
os.makedirs(SAVE_DIR, exist_ok=True)

print("iCloud から写真をダウンロード中...")

# iCloud の写真をすべて取得（全件取得するので件数が多い場合は注意）
photos = api.photos.all

for photo in photos:
    filename = photo.filename
    # 保存先のパス（重複しないようにチェック）
    file_path = os.path.join(SAVE_DIR, filename)
    if os.path.exists(file_path):
        print(f"{filename} は既にダウンロード済みです。")
        continue

    print(f"Downloading {filename}...")
    try:
        # ダウンロード（download() はレスポンスオブジェクトのようなものを返す）
        with open(file_path, "wb") as f:
            f.write(photo.download().raw.read())
    except Exception as e:
        print(f"ダウンロード中にエラーが発生しました: {e}")

print("ダウンロード完了！")
