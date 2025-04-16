
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# GitHubのユーザー情報を取得
github_username = os.getenv("username")
print("GitHubのユーザー名:", github_username)
if not github_username:
    print("環境変数 'username' が設定されていません")
    exit()
    
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
    "X-API-KEY": "super-secret-key"
}

# 自分のAPIへPOST
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
response = requests.post("http://127.0.0.1:8000/github/", json=payload, headers=headers)

print("自分のAPIの応答:", response.json())
