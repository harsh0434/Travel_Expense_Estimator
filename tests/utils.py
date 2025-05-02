import json
from datetime import datetime, timedelta
from functools import wraps
import jwt
from firebase_admin import auth
from .factories import UserFactory, FirebaseUserFactory

def generate_test_token(user_data=None):
    """Generate a test JWT token."""
    if user_data is None:
        user_data = FirebaseUserFactory()
    
    payload = {
        'uid': user_data['uid'],
        'email': user_data['email'],
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'aud': 'travel-cost-estimator',
        'iss': 'https://securetoken.google.com/travel-cost-estimator',
        'sub': user_data['uid']
    }
    
    return jwt.encode(payload, 'test-secret', algorithm='HS256')

def mock_firebase_verify_token(token):
    """Mock Firebase token verification."""
    try:
        payload = jwt.decode(token, 'test-secret', algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        raise auth.InvalidIdTokenError('Invalid token')

def with_auth(f):
    """Decorator to add authentication headers to test requests."""
    @wraps(f)
    def wrapper(client, *args, **kwargs):
        user_data = FirebaseUserFactory()
        token = generate_test_token(user_data)
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        return f(client, *args, headers=headers, **kwargs)
    return wrapper

def assert_json_response(response, status_code=200):
    """Assert that the response is JSON and has the expected status code."""
    assert response.status_code == status_code
    assert response.content_type == 'application/json'
    return json.loads(response.data)

def create_test_user():
    """Create a test user with Firebase credentials."""
    user_data = UserFactory()
    firebase_user = FirebaseUserFactory(
        email=user_data['email'],
        display_name=user_data['display_name']
    )
    return user_data, firebase_user

def mock_firebase_auth_error(error_code='INVALID_ID_TOKEN'):
    """Create a mock Firebase authentication error."""
    class MockFirebaseError(Exception):
        def __init__(self):
            self.code = error_code
            self.message = f'Firebase Auth Error: {error_code}'
    return MockFirebaseError()

def parse_pagination_headers(response):
    """Parse pagination headers from response."""
    return {
        'total': int(response.headers.get('X-Total-Count', 0)),
        'page': int(response.headers.get('X-Page', 1)),
        'per_page': int(response.headers.get('X-Per-Page', 10)),
        'total_pages': int(response.headers.get('X-Total-Pages', 1))
    }

def assert_valid_schema(data, schema):
    """Assert that data matches the expected schema."""
    def _validate_type(value, expected_type):
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        return False

    for key, expected_type in schema.items():
        assert key in data, f"Missing key: {key}"
        assert _validate_type(data[key], expected_type), f"Invalid type for {key}: expected {expected_type}"

def create_test_travel_history(user_id, num_entries=5):
    """Create test travel history entries for a user."""
    from .factories import TravelHistoryFactory
    return [
        TravelHistoryFactory(user_id=user_id)
        for _ in range(num_entries)
    ]

def setup_mock_firebase_admin(monkeypatch):
    """Set up mock Firebase Admin SDK."""
    def mock_verify_id_token(token, **kwargs):
        return mock_firebase_verify_token(token)

    def mock_get_user(uid):
        return FirebaseUserFactory(uid=uid)

    monkeypatch.setattr(auth, 'verify_id_token', mock_verify_id_token)
    monkeypatch.setattr(auth, 'get_user', mock_get_user)

def compare_datetime(dt1, dt2, tolerance_seconds=1):
    """Compare two datetimes with a tolerance."""
    if isinstance(dt1, str):
        dt1 = datetime.fromisoformat(dt1.replace('Z', '+00:00'))
    if isinstance(dt2, str):
        dt2 = datetime.fromisoformat(dt2.replace('Z', '+00:00'))
    
    difference = abs((dt1 - dt2).total_seconds())
    return difference <= tolerance_seconds 