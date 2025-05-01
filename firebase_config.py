import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_firebase():
    try:
        # Initialize Firebase Admin SDK with credentials from environment variables
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        })
        
        # Initialize the app
        firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        db = firestore.client()
        
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return None

# Initialize Firebase and get the database client
db = initialize_firebase() 