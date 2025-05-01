"""Test configuration settings."""

# Test environment settings
TEST_ENV = {
    'TESTING': True,
    'DEBUG': True,
    'SECRET_KEY': 'test-secret-key',
    'FIREBASE_PROJECT_ID': 'test-project',
    'FIREBASE_PRIVATE_KEY_ID': 'test-key-id',
    'FIREBASE_PRIVATE_KEY': 'test-private-key',
    'FIREBASE_CLIENT_EMAIL': 'test@example.com',
    'FIREBASE_CLIENT_ID': 'test-client-id',
    'FIREBASE_AUTH_URI': 'https://accounts.google.com/o/oauth2/auth',
    'FIREBASE_TOKEN_URI': 'https://oauth2.googleapis.com/token',
    'FIREBASE_AUTH_PROVIDER_X509_CERT_URL': 'https://www.googleapis.com/oauth2/v1/certs',
    'FIREBASE_CLIENT_X509_CERT_URL': 'https://www.googleapis.com/robot/v1/metadata/x509/test'
}

# Test user credentials
TEST_USER = {
    'email': 'test@example.com',
    'password': 'test-password',
    'display_name': 'Test User'
}

# Test Firebase configuration
TEST_FIREBASE_CONFIG = {
    'apiKey': 'test-api-key',
    'authDomain': 'test-project.firebaseapp.com',
    'projectId': 'test-project',
    'storageBucket': 'test-project.appspot.com',
    'messagingSenderId': 'test-sender-id',
    'appId': 'test-app-id',
    'measurementId': 'test-measurement-id'
}

# Test data schemas
USER_SCHEMA = {
    'email': 'string',
    'display_name': 'string',
    'created_at': 'string',
    'last_login': 'string'
}

TRAVEL_DATA_SCHEMA = {
    'destination': 'string',
    'duration': 'number',
    'travelers': 'number',
    'accommodation': 'string',
    'activities': 'array',
    'transportation': 'string'
}

ESTIMATE_SCHEMA = {
    'total': 'number',
    'breakdown': 'object'
}

# Test rate limits
RATE_LIMIT = {
    'default': '100 per day',
    'auth': '20 per minute',
    'estimate': '50 per hour'
}

# Test error messages
ERROR_MESSAGES = {
    'auth': {
        'invalid_token': 'Invalid authentication token',
        'expired_token': 'Token has expired',
        'missing_token': 'No authentication token provided',
        'invalid_credentials': 'Invalid email or password'
    },
    'validation': {
        'missing_fields': 'Required fields are missing',
        'invalid_format': 'Invalid data format',
        'invalid_range': 'Value is out of acceptable range'
    },
    'rate_limit': {
        'exceeded': 'Rate limit exceeded. Please try again later.'
    }
}

# Test endpoints
ENDPOINTS = {
    'auth': {
        'login': '/login',
        'signup': '/signup',
        'logout': '/logout'
    },
    'travel': {
        'estimate': '/estimate',
        'history': '/history',
        'recommendations': '/recommendations'
    },
    'user': {
        'profile': '/profile',
        'settings': '/settings'
    }
}

# Test data ranges
DATA_RANGES = {
    'duration': {
        'min': 1,
        'max': 30
    },
    'travelers': {
        'min': 1,
        'max': 10
    },
    'cost': {
        'min': 100,
        'max': 10000
    }
}

# Test categories
ACCOMMODATION_TYPES = ['budget', 'mid-range', 'luxury']
ACTIVITY_TYPES = ['sightseeing', 'dining', 'shopping', 'adventure', 'relaxation', 'cultural']
TRANSPORTATION_TYPES = ['public', 'rental', 'taxi', 'private']

# Test timeouts
TIMEOUTS = {
    'default': 5,  # seconds
    'firebase': 10,
    'estimation': 15
}

# Test pagination
PAGINATION = {
    'default_page': 1,
    'default_per_page': 10,
    'max_per_page': 100
} 