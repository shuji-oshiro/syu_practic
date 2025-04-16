import requests
import os

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_ID = "U1234567890"  # ← 送りたい相手のSlack User ID

def send_message_to_slack(text: str):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": SLACK_USER_ID,
        "text": text
    }

    res = requests.post(url, headers=headers, json=payload)
    print("Slack response:", res.json())


send_message_to_slack("Hello from Python!")
# これを実行することで、指定したSlackユーザーにメッセージを送信することができます。
