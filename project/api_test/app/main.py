# src/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str

fake_tasks = [
    {"id": 1, "title": "勉強する"},
    {"id": 2, "title": "運動する"}
]

@app.get("/api/tasks", response_model=List[Task])
def get_tasks():
    return fake_tasks
