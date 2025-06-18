import os
import tempfile
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.menu_schema import MenusOut

client = TestClient(app)


def test_post_menus():
    # テスト用CSVを一時ファイルに作成
    csv_content = "テストメニュー,500,説明文,てすと\n"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8') as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        response = client.post("/menus", files={"file": ("test.csv", f, "text/csv")})

    os.remove(tmp_path)

    assert response.status_code == 200
    data = response.json()
    menus = [MenusOut(**menu) for menu in response.json()]  # ← これ！

    assert isinstance(data, list)
    assert any(menu.food_name == "テストメニュー" for menu in menus)


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)