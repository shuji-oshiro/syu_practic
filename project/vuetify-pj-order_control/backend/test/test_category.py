from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)




def test_add_category():
    response = client.post("/category", json={
        "name": "Test Category",
        "description": "This is a test category"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 1件のカテゴリが追加されたことを確認

def test_get_categories():
    response = client.get("/category")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # 1件のカテゴリが取得されたことを確認
    assert data[0]["name"] == "Test Category"
    assert data[0]["description"] == "This is a test category"
