<<<<<<< HEAD
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, make_response, session
from predict import TravelCostPredictor
import os
from functools import wraps
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)  # for session management

# Add session configuration
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session lifetime in seconds (1 hour)

# Initialize and train the predictor
predictor = TravelCostPredictor()
if not predictor.train():  # Train the model when the app starts
    print("Warning: Model training failed. Using default model parameters.")

# Load destinations from travel_data.json
with open('data/travel_data.json', 'r') as f:
    travel_data = json.load(f)
    destinations = sorted({entry['destination'] for entry in travel_data['travel_data']})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login')
def login():
    # Don't redirect if already on login page
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html', destinations=destinations)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/auth', methods=['POST'])
def auth():
    try:
        data = request.get_json()
        if data and 'user_id' in data:
            session['user_id'] = data['user_id']
            session.permanent = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Invalid user data'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/check-auth')
def check_auth():
    is_authenticated = 'user_id' in session
    return jsonify({
        'authenticated': is_authenticated,
        'redirect': url_for('home') if is_authenticated else url_for('login')
    })

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['destination', 'days', 'people', 'travel_mode', 'budget_level']):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Get region based on destination
        region = next((entry['region'] for entry in travel_data['travel_data'] 
                      if entry['destination'] == data['destination']), 'north india')
        
        # Make prediction
        result = predictor.predict(
            destination=data['destination'],
            region=region,
            days=int(data['days']),
            people=int(data['people']),
            travel_mode=data['travel_mode'],
            budget_level=data['budget_level']
        )
        
        if result:
            return jsonify({
                'success': True,
                'total_trip_cost': result['total_trip_cost'],
                'per_person_per_day': result['per_person_per_day'],
                'cost_breakdown': result['cost_breakdown'],
                'destination_info': result['destination_info'],
                'confidence': result['confidence']
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to make prediction'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('history.html')

@app.after_request
def set_security_headers(response):
    # Security: Use CSP instead of X-Frame-Options
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self';"
    # Remove deprecated headers if present
    response.headers.pop('X-Frame-Options', None)
    response.headers.pop('X-XSS-Protection', None)
    # Remove Expires header if present
    response.headers.pop('Expires', None)
    return response

@app.route('/static/<path:path>')
def serve_static(path):
    response = make_response(send_from_directory('static', path))
    # Performance: Set cache-control for static assets
    if path.endswith(('.css', '.js', '.woff2', '.woff', '.ttf', '.eot', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    # Set correct font MIME types
    if path.endswith('.woff2'):
        response.headers['Content-Type'] = 'font/woff2'
    elif path.endswith('.woff'):
        response.headers['Content-Type'] = 'font/woff'
    elif path.endswith('.ttf'):
        response.headers['Content-Type'] = 'font/ttf'
    elif path.endswith('.eot'):
        response.headers['Content-Type'] = 'application/vnd.ms-fontobject'
    elif path.endswith('.svg'):
        response.headers['Content-Type'] = 'image/svg+xml'
    return response

if __name__ == '__main__':
    print("Server starting! Access the travel calculator at: http://127.0.0.1:5000")
    app.run(debug=True) 
=======
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import os
from functools import wraps
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from flask_talisman import Talisman
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import pandas as pd
from firebase_config import db
from firebase_admin import auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# Initialize Talisman for HTTPS
Talisman(app,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "www.gstatic.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'", "https://*.firebaseio.com"]
    }
)

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP_PASSWORD')
mail = Mail(app)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, uid, email, email_verified=False):
        self.id = uid
        self.email = email
        self.email_verified = email_verified

    @staticmethod
    def get(user_id):
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return User(
                uid=user_doc.id,
                email=user_data.get('email'),
                email_verified=user_data.get('email_verified', False)
            )
        return None

# Load or create ML model
def load_or_create_model():
    try:
        model = joblib.load('travel_model.joblib')
    except:
        model = RandomForestRegressor(n_estimators=100)
        X = np.random.rand(1000, 4)
        y = np.random.rand(1000) * 5000
        model.fit(X, y)
        joblib.dump(model, 'travel_model.joblib')
    return model

model = load_or_create_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Sign in with Firebase
            user = auth.get_user_by_email(email)
            if user:
                user_obj = User.get(user.uid)
                if user_obj and not user_obj.email_verified:
                    flash('Please verify your email first.')
                    return redirect(url_for('login'))
                
                login_user(user_obj)
                return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password
            )
            
            # Store additional user data in Firestore
            db.collection('users').document(user.uid).set({
                'email': email,
                'email_verified': False,
                'created_at': datetime.utcnow()
            })
            
            # Send verification email
            send_verification_email(email)
            
            flash('Please check your email for verification code')
            return redirect(url_for('verify'))
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            flash('Error creating account')
    return render_template('signup.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email = request.form.get('email')
        email_code = request.form.get('email_code')
        
        if verify_code(email, email_code):
            try:
                user = auth.get_user_by_email(email)
                db.collection('users').document(user.uid).update({
                    'email_verified': True
                })
                flash('Verification successful! Please login.')
                return redirect(url_for('login'))
            except Exception as e:
                logger.error(f"Verification error: {str(e)}")
                flash('Error verifying account')
        else:
            flash('Invalid verification code')
    return render_template('verify.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/estimate', methods=['POST'])
@login_required
def estimate_travel_cost():
    try:
        data = request.get_json()
        features = np.array([
            float(data['duration']),
            float(data['season']),
            float(data['accommodation_type']),
            float(data['destination'])
        ]).reshape(1, -1)
        
        estimated_cost = model.predict(features)[0]
        
        # Save to Firestore
        db.collection('travel_history').add({
            'user_id': current_user.id,
            'destination': data['destination'],
            'duration': data['duration'],
            'season': data['season'],
            'accommodation_type': data['accommodation_type'],
            'estimated_cost': estimated_cost,
            'created_at': datetime.utcnow()
        })
        
        return jsonify({
            'success': True,
            'estimated_cost': float(estimated_cost)
        })
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history')
@login_required
def travel_history():
    history = db.collection('travel_history').where('user_id', '==', current_user.id).get()
    history_data = []
    for doc in history:
        data = doc.to_dict()
        data['id'] = doc.id
        history_data.append(data)
    return render_template('history.html', history=history_data)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Helper functions
def send_verification_email(email):
    try:
        code = ''.join(random.choices(string.digits, k=6))
        session['email_code'] = code
        msg = Message('Travel Expense Estimator - Email Verification',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[email])
        msg.body = f'Your verification code is: {code}'
        mail.send(msg)
        logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")

def verify_code(email, code):
    return code == session.get('email_code')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

if __name__ == '__main__':
    ssl_context = (
        'certificates/certificate.crt',
        'certificates/private.key'
    )
    app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True) 
>>>>>>> 8986d4d62c016c7d82b559e4d11cab328e04b080
