import json, csv, os
from typing import List
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sendmail import send_email
import asyncio

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

TASK_FILE = os.path.join(DATA_DIR, "tasks.json")
USER_FILE = os.path.join(DATA_DIR, "users.json")



def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)

    
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    # with open(USER_FILE, newline='', encoding='utf-8') as f:
    #     reader = csv.DictReader(f)
    #     return [row for row in reader]  # username, email 付きで返す

def check_and_notify_tasks():
    asyncio.run(_check_and_notify_tasks_async())  # 同期関数内で安全に呼び出す

async def _check_and_notify_tasks_async():
    tasks = load_tasks()
    today = datetime.today().date().isoformat()

    for task in tasks:
        print(f"[DEBUG] _check_and_notify_tasks_async time:{datetime.now()} task_name:{task['title']}")
        
        tolist = []
        for user in task["users"]:
            tolist.append(user["email"])

        await send_email(
            to=tolist,
            subject=f"[Reminder] タスク：{task['title']} 期限：{task['due_date']}",
            content=f"タスク「{task['title']}」が未完了。"
        )

