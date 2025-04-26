# tests/test_main.py


def test_get_all_tasks(client):
    response = client.get("/task")
    assert response.status_code == 200 


def test_add_task_and_delete(client):
    response = client.post("/task", params={
    "title": "テストタスク",
    "due_date": "2025-05-01"
    })
    assert response.status_code == 200
    assert response.json()
    task = response.json()

    task_id = task["id"]
# def test_complete_task_for_user(client):
    # タスクに対して 1人を完了（削除）
    target_username = task["users"][0]["username"]
    response = client.delete(f"/task/{task_id}/user/{target_username}")
    assert response.status_code == 200
    assert response.json()
    
# def test_delete_task(client):
    # 最後はテスト用タスクを削除
    response = client.delete(f"/task/{task_id}")
    assert response.status_code == 200