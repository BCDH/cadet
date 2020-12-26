from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_open():
    response = client.get("/")
    assert response.status_code == 200
    

def test_read_main_no_password():
    response = client.get("/main")
    assert response.status_code == 401
  
def test_create_language():
    pass
    #assert that works with various problems

def test_clone_language():
    pass
    #assert that works for all existing languages and their dependencies