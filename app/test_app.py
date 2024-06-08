import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_main(client):
    response = client.get('/main')
    assert response.status_code == 200


def test_view_db(client):
    response = client.get('/view_db')
    assert response.status_code == 202
