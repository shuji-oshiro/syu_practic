import logging
from app.src.main import app
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)

client = TestClient(app)

def test_read_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World"}
    logger.info("レスポンスボディ: %s", response.json())


def test_get_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    logger.info("レスポンスボディ: %s", response.json())


