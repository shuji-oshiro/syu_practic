import os
import sys
import pytz
import uuid
import logging
import datetime
import json, csv
from typing import List
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ロギングの設定
# ロガーの作成
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# フォーマッターの設定
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)

# タイムゾーンを日本時間に設定
formatter.converter = lambda *args: datetime.datetime.now(pytz.timezone('Asia/Tokyo')).timetuple()

# テスト実行中でない場合のみファイルハンドラーを追加
if not sys.modules.get('pytest'):
    # ファイルハンドラーの作成
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# コンソールハンドラーは常に追加
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)



app = FastAPI()

# CORS許可（フロントエンドと連携）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# パス設定
TASK_FILE = Path("data/tasks.json")
USER_FILE = Path("data/user.csv")

# データモデル
class Task(BaseModel):
    id: str
    name: str
    date: str

class User(BaseModel):
    name: str
    email: str

json_data = None

# タスク一覧を取得
@app.get("/api/tasks", response_model=List[Task])
def get_tasks():

    logger.info("タスク一覧取得開始")
    try:
        if not TASK_FILE.exists():
            return []
        
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
            
            json_data = json.loads(content)
            return json_data
        
    except Exception as e:
        logger.error(f"タスク一覧取得エラー: {e}")
        return []

# タスク追加
@app.post("/api/tasks")
def add_task(task: dict):
    logger.info(f"タスク追加開始: {task}")
    
    task_list = get_tasks()
    task_id = str(uuid.uuid4())
    new_task = {"id": task_id, "name": task["name"], "date": task["date"]}
    task_list.append(new_task)
    
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(task_list, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "id": task_id}

# タスク削除
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    tasks = get_tasks()
    new_tasks = [task for task in tasks if task["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(new_tasks, f, indent=2, ensure_ascii=False)
    return {"status": "deleted"}

# タスクに紐づくユーザー一覧
@app.get("/api/tasks/{task_id}/users", response_model=List[User])
def get_users_for_task(task_id: str):
    if not USER_FILE.exists():
        raise HTTPException(status_code=404, detail="ユーザーデータが存在しません")
    users = []
    with open(USER_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append({"name": row["name"], "email": row["email"]})
    return users
