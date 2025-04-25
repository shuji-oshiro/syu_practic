# tests/test_main.py

def test_get_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "勉強する"
