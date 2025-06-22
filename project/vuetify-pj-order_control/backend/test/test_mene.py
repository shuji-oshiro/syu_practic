from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_add_menu():
    response = client.put("/menu", json={
        "name": "テストメニュー",
        "price": 1000, 
        "description": "テストの説明",
        "search_text": "てすとめにゅー"})
    
    assert response.status_code == 200

def test_add_menu2():
    response = client.put("/menu", json={
        "name": "テストメニュー2",
        "price": 2000, 
        "description": "テストの説明22",
        "search_text": "てすとめにゅー222"})
    
    assert response.status_code == 200

def test_get_menus():
    response = client.get("/menu")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_menus_byid():
    response = client.get("/menu/2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_update_menu():
    response = client.patch("/menu/", json={
        "menu_id": 2,
        "name": "更新されたメニュー",
        "price": 1500,
        "description": "更新された説明",
        "search_text": "こうしんされためにゅー"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_get_menus_2():
    response = client.get("/menu")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)



def test_add_order():
    response = client.put("/order", json={
        "seat_id": 1,
        "menu_id": 1, 
        "order_cnt": 2})
    
    assert response.status_code == 200

# def test_add_order2():
#     response = client.put("/order", json={
#         "seat_id": 1,
#         "menu_id": 2, 
#         "order_cnt": 3})
    
#     assert response.status_code == 200

def test_get_orders():
    response = client.get("/order/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)