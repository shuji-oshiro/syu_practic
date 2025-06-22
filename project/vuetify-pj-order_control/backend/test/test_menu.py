from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_import_menu():
    response = client.post("/menu", json={
        "file_path": "backend/test/test_menu.csv"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 14  # CSVからメニューが読み込まれたことを確認

def test_add_menu():
    response = client.put("/menu", json={
        "name": "かつ丼",
        "price": 1000,
        "description": "美味しいかつ丼です",
        "search_text": "かつどん"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15 # 新しいメニューが追加されたことを確認

def test_get_menus_byid():
    response = client.get("/menu/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict) # レスポンスが辞書型であることを確認


def test_update_menu():
    response = client.patch("/menu/", json={
        "menu_id": 1,
        "name": "天丼",
        "price": 1200,
        "description": "美味しい天丼です",
        "search_text": "てんどん"
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15 # メニューの件数に変更がないことを確認

def test_delete_menu():
    response = client.delete("/menu/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 14  # メニューが削除されたことを確認


def test_add_order1():
    response = client.post("/order", json=[
        {
            "seat_id": 1,
            "menu_id": 2,
            "order_cnt": 2
        }
    ])
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 2件の注文が追加されたことを確認

def test_add_order2():
    response = client.post("/order", json=[
        {
            "seat_id": 2,
            "menu_id": 2,
            "order_cnt": 2
        },
        {
            "seat_id": 2,
            "menu_id": 3,
            "order_cnt": 1
        }
    ])
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # 2件の注文が追加されたことを確認


def test_get_orders():
    response = client.get("/order/2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # 指定したシートの注文が2件のであることを確認

def test_delete_order():
    response = client.delete("/order/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0 # 注文が1件削除されたことを確認