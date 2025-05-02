import pytest
from app import app

def test_login_page():
    with app.test_client() as client:
        response = client.get('/login')
        assert response.status_code == 200
        assert b'TravelMint' in response.data 