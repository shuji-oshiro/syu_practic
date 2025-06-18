import os
import tempfile
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.menu_schema import MenuOut,MenuIn, MenuUpdate

client = TestClient(app)

delite_menus_id = []


def test_post_menus():
    # テスト用CSVを一時ファイルに作成
    csv_content = "テストメニュー,500,説明文,てすと\nテストメニュー2,600,説明文2,てすと2\n"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8') as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        response = client.post("/menus", files={"file": ("test.csv", f, "text/csv")})

    os.remove(tmp_path)

    assert response.status_code == 200
    data = response.json()
    menus = [MenuOut(**menu) for menu in response.json()] 

    assert isinstance(data, list)
    assert len(menus) == 2   # メニューが2件存在することを確認


def test_add_menus():
    new_menu = MenuIn(
        food_name="新しいメニュー",
        unit_price=800,
        descrption="新しいメニューの説明",
        search_text="新しいメニュー"
    )
    
    response = client.put("/menus", json=new_menu.dict())
    assert response.status_code == 200
    data = response.json()
    menus = [MenuOut(**menu) for menu in data] 

    assert isinstance(data, list)
    assert any(menu.food_name == "新しいメニュー" for menu in menus)


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200
    menus = [MenuOut(**menu) for menu in response.json()] 
    assert len(menus) == 3  # メニューが3件存在することを確認
    delite_menus_id.extend([menu.menu_id for menu in menus])  # 削除用のIDを保存


def test_get_menus_menuid():
    target_id = delite_menus_id.pop()  # 最初のメニューIDを取得
    response = client.get("/menus", params={"menu_id": target_id})
    assert response.status_code == 200
    menus = [MenuOut(**menu) for menu in response.json()] 
    assert len(menus) == 1  # メニューが1件であることを確認


def test_get_menus_menuid_Nodata():
    response = client.get("/menus", params={"menu_id": 9999})  # 存在しないIDを指定
    assert response.status_code == 200
    menus = [MenuOut(**menu) for menu in response.json()] 
    assert len(menus) == 0  # メニューが0件であることを確認


def test_update_menus():
    target_id = delite_menus_id.pop()
    update_menu = MenuUpdate(
        menu_id=target_id,
        food_name="更新されたメニュー",
        unit_price=1000,
        descrption="更新された説明",
        search_text="更新された検索テキスト"
    )
    
    response = client.patch("/menus", json=update_menu.dict())
    assert response.status_code == 200
    data = response.json()
    menus = [MenuOut(**menu) for menu in data] 

    assert isinstance(data, list)
    assert any(menu.food_name == "更新されたメニュー" for menu in menus) # 更新されたメニューが存在することを確認


def test_delete_menus():
    target_id = delite_menus_id.pop()  # 削除するメニューIDを取得
    response = client.delete("/menus", params={"menu_id": target_id})  # メニューID 1 を削除
    assert response.status_code == 200
    data = response.json()
    menus = [MenuOut(**menu) for menu in data] 

    assert isinstance(data, list)
    assert len(menus) == 2  # メニューが1件削除されていることを確認


