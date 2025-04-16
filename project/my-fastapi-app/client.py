# coding: utf-8
# GitHubのユーザー情報を取得し、自分のFastAPIにPOSTするクライアントコード
# これはPythonのrequestsライブラリを使用して実装されています。
# 事前にrequestsライブラリをインストールしておく必要があります。   
# pip install requests
# 例: GitHubのユーザー名を指定して、そのユーザーの公開リポジトリ数を取得し、自分のFastAPIにPOSTする
# 自分のFastAPIは、POSTリクエストを受け取り、リクエストボディに含まれるデータを処理します。
# FastAPIのエンドポイントは、/github/でPOSTリクエストを受け取ります。
import requests
import os
# GitHubのユーザー情報を取得
github_username = "shuji-oshiro"
github_url = f"https://api.github.com/users/{github_username}"
github_response = requests.get(github_url)

if github_response.status_code != 200:
    print("GitHub APIから情報を取得できませんでした")
    exit()

github_data = github_response.json()
print("GitHubから取得:", github_data)
# 自分のFastAPIに送るデータを構成
payload = {
    "login": github_data["login"],
    "public_repos": github_data["public_repos"]
}

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "super-secret-key" # 自分のAPIキーをここに設定
    #"X-API-KEY": os.getenv("API_KEY") # .envから取得する場合
}

# 自分のAPIへPOST
response = requests.post("http://127.0.0.1:8000/github/", json=payload, headers=headers)

print("自分のAPIの応答:", response.json())
