import os
import requests

os.environ['NO_PROXY'] = '127.0.0.1,localhost' # これを追加することで、localhostへのリクエストがプロキシを通らないようにする
url = "http://127.0.0.1:8000/process/"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "super-secret-key",  # .envに設定したキー
}
payload = {
    "name": "ケン",
    "age": 28
}

#response = requests.post(url, json=payload, headers=headers)
response = requests.post(url, json=payload, headers=headers)
print("Status:", response.status_code)
print("Text:", response.text)

print("Status Code:", response.status_code)
print("Response:", response.json())
