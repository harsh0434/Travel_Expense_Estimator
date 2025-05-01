import pytest
from app import app as flask_app
import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Set up test configuration
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
    })

    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Generate authentication headers for protected routes."""
    return {
        'Authorization': 'Bearer test-token'
    }

@pytest.fixture
def mock_firebase_admin(monkeypatch):
    """Mock Firebase Admin SDK initialization."""
    def mock_init_app(*args, **kwargs):
        return None

    def mock_verify_id_token(*args, **kwargs):
        return {
            'uid': 'test-user-id',
            'email': 'test@example.com'
        }

    monkeypatch.setattr(firebase_admin, 'initialize_app', mock_init_app)
    monkeypatch.setattr(auth, 'verify_id_token', mock_verify_id_token)

@pytest.fixture
def sample_travel_data():
    """Sample travel data for testing."""
    return {
        'destination': 'Paris',
        'duration': 7,
        'travelers': 2,
        'accommodation': 'mid-range',
        'activities': ['sightseeing', 'dining'],
        'transportation': 'public'
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'test-password',
        'display_name': 'Test User'
    }

@pytest.fixture
def authenticated_client(client, auth_headers):
    """A test client with authentication headers."""
    def _authenticated_client(*args, **kwargs):
        headers = kwargs.pop('headers', {})
        headers.update(auth_headers)
        return client(*args, headers=headers, **kwargs)
    return _authenticated_client

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database operations."""
    class MockDB:
        def __init__(self):
            self.data = {}

        def collection(self, name):
            if name not in self.data:
                self.data[name] = {}
            return MockCollection(self.data[name])

    class MockCollection:
        def __init__(self, data):
            self.data = data

        def document(self, doc_id):
            if doc_id not in self.data:
                self.data[doc_id] = {}
            return MockDocument(self.data[doc_id])

        def where(self, field, op, value):
            return self

        def get(self):
            return [MockDocument(data) for data in self.data.values()]

    class MockDocument:
        def __init__(self, data):
            self.data = data

        def set(self, data):
            self.data.update(data)
            return self

        def get(self):
            return self

        def to_dict(self):
            return self.data

    db = MockDB()
    monkeypatch.setattr('firebase_admin.firestore.client', lambda: db)
    return db

@pytest.fixture
def cleanup_test_data():
    """Cleanup test data after tests."""
    yield
    # Add cleanup logic here if needed 