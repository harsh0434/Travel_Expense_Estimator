from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session, flash
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
import twilio
from twilio.rest import Client
from flask_talisman import Talisman

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

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')  # Change this in production

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

# Force HTTPS
@app.before_request
def before_request():
    if not request.is_secure and os.environ.get('FLASK_ENV') == 'production':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your-app-password')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your-account-sid')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your-auth-token')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', 'your-twilio-number')
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Mock user database (for testing)
users_db = {}

# Verification codes storage
verification_codes = {}

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = "Email Verification Code"
    
    body = f"Your verification code is: {code}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        return False

def send_verification_sms(phone_number, code):
    try:
        message = twilio_client.messages.create(
            body=f"Your verification code is: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        return False

@app.route('/send-verification', methods=['POST'])
def send_verification():
    try:
        data = request.get_json()
        email = data.get('email')
        phone_number = data.get('phone_number')
        
        if not email and not phone_number:
            return jsonify({'error': 'Email or phone number is required'}), 400
            
        verification_data = {}
        
        if email:
            email_code = generate_verification_code()
            if send_verification_email(email, email_code):
                verification_data['email_code'] = email_code
            else:
                return jsonify({'error': 'Failed to send email verification'}), 500
                
        if phone_number:
            sms_code = generate_verification_code()
            if send_verification_sms(phone_number, sms_code):
                verification_data['sms_code'] = sms_code
            else:
                return jsonify({'error': 'Failed to send SMS verification'}), 500
                
        verification_codes[email or phone_number] = verification_data
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Verification sending error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/verify-code', methods=['POST'])
def verify_code():
    try:
        data = request.get_json()
        email = data.get('email')
        phone_number = data.get('phone_number')
        email_code = data.get('email_code')
        sms_code = data.get('sms_code')
        
        if not email and not phone_number:
            return jsonify({'error': 'Email or phone number is required'}), 400
            
        stored_codes = verification_codes.get(email or phone_number)
        if not stored_codes:
            return jsonify({'error': 'No verification codes found'}), 400
            
        if email_code and stored_codes.get('email_code') != email_code:
            return jsonify({'error': 'Invalid email verification code'}), 400
            
        if sms_code and stored_codes.get('sms_code') != sms_code:
            return jsonify({'error': 'Invalid SMS verification code'}), 400
            
        # Clear verification codes after successful verification
        del verification_codes[email or phone_number]
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Code verification error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if session.get('user'):
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user'):
            return redirect(url_for('home'))
        return render_template('login.html')
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Check if user exists
        if email not in users_db:
            return jsonify({'error': 'Invalid email or password'}), 401

        user_data = users_db[email]
        
        # Verify password
        if not check_password_hash(user_data['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Set session
        session['user'] = {
            'email': email,
            'name': user_data.get('name', '')
        }

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400

        # Check if user already exists
        if email in users_db:
            return jsonify({'error': 'Email already registered'}), 400

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user
        users_db[email] = {
            'name': name,
            'password': hashed_password,
            'created_at': datetime.now()
        }

        # Set session
        session['user'] = {
            'email': email,
            'name': name
        }

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'An error occurred during signup'}), 500

@app.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Create user if not exists
        if email not in users_db:
            users_db[email] = {
                'name': name,
                'created_at': datetime.now()
            }

        # Set session
        session['user'] = {
            'email': email,
            'name': name
        }

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        return jsonify({'error': 'An error occurred during Google login'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/calculator')
@login_required
def calculator():
    return render_template('calculator.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/destinations')
@login_required
def destinations():
    return render_template('destinations.html')

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug log
        
        # Extract data from request
        destination = data.get('destination', '').lower()
        days = int(data.get('days', 0))
        people = int(data.get('people', 0))
        travel_mode = data.get('travel_mode', '').lower()
        budget_level = data.get('budget_level', '').lower()
        
        # Validate inputs
        if not all([destination, days, people, travel_mode, budget_level]):
            return jsonify({
                'error': 'Please fill in all required fields'
            }), 400
            
        if days < 1 or days > 30:
            return jsonify({
                'error': 'Number of days must be between 1 and 30'
            }), 400
            
        if people < 1 or people > 10:
            return jsonify({
                'error': 'Number of people must be between 1 and 10'
            }), 400
        
        # Mock prediction for testing
        predicted_costs = {
            'accommodation': 1000,
            'food': 500,
            'transportation': 800,
            'activities': 300
        }
        
        # Calculate total cost
        daily_total = sum(predicted_costs.values())
        total_cost = daily_total * days * people
        
        # Create history data
        history_data = {
            'userId': session['user']['email'],
            'destination': destination,
            'region': 'north india',  # Mock region
            'days': days,
            'people': people,
            'travelMode': travel_mode,
            'budgetLevel': budget_level,
            'dailyCost': daily_total,
            'totalCost': total_cost,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'predicted_costs': predicted_costs,
            'daily_total': daily_total,
            'total_cost': total_cost,
            'history_data': history_data
        })
            
    except ValueError as e:
        print(f"Value error: {e}")
        return jsonify({
            'error': 'Please check your input values and try again.'
        }), 400
    except Exception as e:
        print(f"Error making prediction: {e}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    ssl_context = (
        'certificates/certificate.crt',
        'certificates/private.key'
    )
    print("Server starting! Access the travel calculator at: https://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True) 