import pytest
from app import app, predictor
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 302  # Should redirect to login

def test_login_page(client):
    rv = client.get('/login')
    assert rv.status_code == 200

def test_login_post(client):
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    rv = client.post('/login', 
                    data=json.dumps(data),
                    content_type='application/json')
    assert rv.status_code == 200

def test_signup_post(client):
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }
    rv = client.post('/signup',
                    data=json.dumps(data),
                    content_type='application/json')
    assert rv.status_code == 200

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b'healthy' in rv.data

def test_calculator_route(client):
    response = client.get('/calculator')
    assert response.status_code == 302  # Should redirect to login when not authenticated

def test_predict_endpoint(client):
    test_data = {
        'destination': 'delhi',
        'days': 5,
        'people': 2,
        'travel_mode': 'train',
        'budget_level': 'budget'
    }
    response = client.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
    assert response.status_code == 302  # Should redirect to login when not authenticated

def test_predictor_model():
    # Test the predictor model directly
    test_input = {
        'destination': 'delhi',
        'days': 5,
        'people': 2,
        'travel_mode': 'train',
        'budget_level': 'budget'
    }
    try:
        result = predictor.predict(**test_input)
        assert isinstance(result, dict)
        assert all(isinstance(v, (int, float)) for v in result.values())
    except Exception as e:
        pytest.fail(f"Prediction failed: {str(e)}")

def test_backup_route(client):
    response = client.post('/admin/backup')
    assert response.status_code == 302  # Should redirect to login when not authenticated

def test_restore_route(client):
    response = client.post('/admin/restore', data={'backup_name': 'test_backup'})
    assert response.status_code == 302  # Should redirect to login when not authenticated 