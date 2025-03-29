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