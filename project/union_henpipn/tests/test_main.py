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
    json_data = response.get_json()


def test_store_details(client):
    # まずデータアップロード
    data = (
        "取引先名,店舗名,商品名,売上金額,売上数量,返品金額,返品数量\n"
        "A社,渋谷店,商品X,1000,2,0,0\n"
        "A社,渋谷店,商品Y,500,1,0,0\n"
    )
    client.post('/upload', data={
        'file': (io.BytesIO(data.encode()), 'sales.csv')
    }, content_type='multipart/form-data')

    # 詳細取得テスト
    response = client.get('/details?store=渋谷店')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'products' in json_data
    #assert any(product['product_name'] == '商品X' for product in json_data['products'])
