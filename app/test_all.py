from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_open():
    response = client.get("/")
    assert response.status_code == 200
    #assert response.json() == {"msg": "Hello World"}

def test_read_main_no_password():
    response = client.get("/main")
    assert response.status_code == 401
  