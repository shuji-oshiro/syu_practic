from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.menu_schema import MenuOut,MenuIn, MenuUpdate


client = TestClient(app)

def test_creat_user():
    response = client.post("/users", json={"name": "aaaa", "email": "aaa@aaa.com"})
    assert response.status_code == 200

def test_acceccs_menus():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)