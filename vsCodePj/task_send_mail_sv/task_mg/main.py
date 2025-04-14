# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:29:59 2025

@author: owner-pc


"""

import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
from tkcalendar import DateEntry
#import autoMail_from_appPass


TASKS_FILE = "tasks.json"
user_l = {"user_1":"user_1@gmail.com","user_2":"user_2@gmail.com","user_3":"user_3@gmail.com"}

def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def add_task():
    day_val = entry_day.get()
    task = task_entry.get()
    if task:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_list.insert(tk.END, f"{day_val} - {task}")
        tasks.append({"id":now, "datetime": day_val, "task": task, "users":user_l.copy()})
        save_tasks(tasks)
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("入力エラー", "タスクを入力してください。")

def delete_task():
    selected_index = task_list.curselection()
    if selected_index:
        index = selected_index[0]
        del tasks[index]
        save_tasks(tasks)
        
        task_list.delete(index)
        user_list.delete(0, tk.END)
    else:
        messagebox.showwarning("削除エラー", "削除するタスクを選択してください。")
        
def on_task_select(event):
    selected_index = task_list.curselection()
    if selected_index:
        index = selected_index[0]
        selected_task = tasks[index]
        #task_label.config(text=f"選択中: {selected_task['datetime']} - {selected_task['task']}")
        l = selected_task["users"]
        user_list.delete(0, tk.END)
        
        for key in l.keys():
            user_list.insert(tk.END, f"{key}: {l[key]}")

def delete_user():
    selected_index = task_list.curselection()
    selected_index_user = user_list.curselection()
    

    if selected_index_user:
        index1 = selected_index[0]
        index2 = selected_index_user[0]
        key,val = user_list.get(index2).split(":")        
        
        del tasks[index1]["users"][key]
        save_tasks(tasks)
        user_list.delete(index2)
    else:
        messagebox.showwarning("削除エラー", "タスク完了のユーザを選択してください。")
    pass


app = tk.Tk()
app.title("タスク管理アプリ")

frame = tk.Frame(app)
frame.pack(pady=10)

entry_day = DateEntry(frame,date_pattern="yyyy年mm月dd日")
entry_day.pack(side=tk.LEFT,padx=5)
task_entry = tk.Entry(frame, width=40)
task_entry.pack(side=tk.LEFT, padx=5)

add_button = tk.Button(frame, text="追加", command=add_task)
add_button.pack(side=tk.LEFT)

task_list = tk.Listbox(app, width=60, height=15,exportselection=False)
task_list.pack(pady=10)
# リストボックスの選択時イベントをバインド
task_list.bind("<<ListboxSelect>>", on_task_select)

delete_button = tk.Button(app, text="選択したタスクを削除", command=delete_task)
delete_button.pack()

user_list = tk.Listbox(app, width=60, height=10,exportselection=False)
user_list.pack(pady=10)
delete_user_btn = tk.Button(app, text="タスク完了", command=delete_user)
delete_user_btn.pack()



tasks = load_tasks()
for task in tasks:
    task_list.insert(tk.END, f"{task['datetime']} - {task['task']}")


if __name__ == "__main__":
    app.mainloop()