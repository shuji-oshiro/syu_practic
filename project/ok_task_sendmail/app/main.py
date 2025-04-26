import os
import asyncio
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
# from models import Task, User
from scheduler import load_tasks, load_users, save_tasks, check_and_notify_tasks

#app = FastAPI()

scheduler = BackgroundScheduler()



# --- API Endpoints ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[DEBUG] lifespan start")
    
    # .envファイルを読み込む
    load_dotenv()
    TASK_TIME_HOUR = os.getenv("TASK_EXECUTION_TIME_H")
    TASK_TIME_MINUTE = os.getenv("TASK_EXECUTION_TIME_M")

    job = scheduler.add_job(check_and_notify_tasks, 'cron', hour=TASK_TIME_HOUR, minute=TASK_TIME_MINUTE)
    #job = scheduler.add_job(check_and_notify_tasks, 'interval', seconds=5)

    scheduler.start()
    print(f"[DEBUG] 次のメール送信予定時刻: {job.next_run_time}")
    
    yield  # ★ここでアプリが本格起動

    print("[DEBUG] lifespan shutdown")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# @app.on_event("startup")
# async def startup_event():
#     schedule_daily_email()


@app.get("/task")
def get_all_tasks():
    return load_tasks()

@app.post("/task")
def add_task(title: str, due_date: date):
    users = load_users()
    if not users:
        raise HTTPException(status_code=400, detail="No users found")
    
    tasks = load_tasks()
    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "due_date": due_date.isoformat(),
        "users": users  # [{"username": "alice", "email": "alice@example.com"}, ...]
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


@app.delete("/task/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    updated_tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(updated_tasks)
    return {"message": f"Task {task_id} deleted"}


@app.delete("/task/{task_id}/user/{username}")
def complete_task_for_user(task_id: int, username: str):
    tasks = load_tasks()
    updated_tasks = []

    for task in tasks:
        if task["id"] == task_id:
            # 該当ユーザーを除いた users リストを作成
            task["users"] = [user for user in task["users"] if user["username"] != username]
            
            if task["users"]:  # まだ他ユーザーが残ってるなら保存
                updated_tasks.append(task)
            # 誰もいなければ削除扱い（append しない）
        else:
            updated_tasks.append(task)

    save_tasks(updated_tasks)
    return {"message": f"User '{username}' completed task {task_id}"}


@app.get("/users")
def get_users():
    return load_users()
    
    

