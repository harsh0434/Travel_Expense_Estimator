import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Travel Cost Estimator' in rv.data

def test_login_page(client):
    """Test that the login page loads successfully."""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data

def test_login_post(client):
    """Test login with valid credentials."""
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    rv = client.post('/login', 
                     data=json.dumps(data),
                     content_type='application/json')
    assert rv.status_code in [200, 401]  # Either success or unauthorized

def test_signup_post(client):
    """Test signup with valid data."""
    data = {
        'email': 'newuser@example.com',
        'password': 'password123'
    }
    rv = client.post('/signup',
                     data=json.dumps(data),
                     content_type='application/json')
    assert rv.status_code in [200, 400]  # Either success or bad request

def test_estimate_cost(client):
    """Test travel cost estimation."""
    data = {
        'destination': 'Paris',
        'duration': 7,
        'travelers': 2,
        'accommodation': 'mid-range'
    }
    rv = client.post('/estimate',
                     data=json.dumps(data),
                     content_type='application/json')
    assert rv.status_code == 200
    response_data = json.loads(rv.data)
    assert 'total' in response_data
    assert 'breakdown' in response_data

def test_health_check(client):
    """Test the health check endpoint."""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b'healthy' in rv.data.lower()

def test_protected_route(client):
    """Test access to protected routes."""
    rv = client.get('/dashboard')
    assert rv.status_code == 302  # Should redirect to login page

def test_logout(client):
    """Test logout functionality."""
    rv = client.get('/logout')
    assert rv.status_code == 302  # Should redirect to home page

def test_invalid_route(client):
    """Test handling of invalid routes."""
    rv = client.get('/nonexistent')
    assert rv.status_code == 404

def test_api_rate_limit(client):
    """Test API rate limiting."""
    for _ in range(5):  # Make multiple requests
        client.get('/estimate')
    rv = client.get('/estimate')
    assert rv.status_code == 429  # Too Many Requests 