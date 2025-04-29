import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)  # ← FastAPIはこれ！


def test_upload_file(client):
    with open('tests/data/test_sales.csv', 'rb') as f:
        files = {'file': ('test_sales.csv', f, 'text/csv')}
    
        response = client.post('/api/upload', files=files)
        assert response.status_code == 200
        json_data = response.json()


def test_store_details(client):
    # まずデータアップロード
    with open('tests/data/test_sales.csv', 'rb') as f:
        files = {'file': ('test_sales.csv', f, 'text/csv')}

        response = client.post('/api/upload', files=files)
        assert response.status_code == 200

    # 詳細取得テスト
    response = client.get('/api/details?store=スカラおろく')
    assert response.status_code == 200
    json_data = response.json()
    
 