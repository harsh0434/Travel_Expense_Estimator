from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, make_response, session
from predict import load_trained_model
import os
import logging
from datetime import timedelta
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)  # Required for session
app.permanent_session_lifetime = timedelta(days=7)  # Session lasts 7 days

# Initialize Firebase Admin with the service account
try:
    cred = credentials.Certificate('firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)
    logging.info('Firebase Admin SDK initialized successfully')
except Exception as e:
    logging.error(f'Failed to initialize Firebase Admin SDK: {str(e)}')
    raise

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated via session
        if 'user_id' not in session:
            logging.info('User not authenticated, redirecting to login')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Get the ID token from the request
            data = request.get_json()
            if not data or 'idToken' not in data:
                logging.error('No ID token provided in request')
                return jsonify({'error': 'No ID token provided'}), 400

            id_token = data['idToken']
            
            # Verify the ID token
            try:
                decoded_token = auth.verify_id_token(id_token)
                user_id = decoded_token['uid']
                email = decoded_token.get('email', '')
                
                # Create a session
                session['user_id'] = user_id
                session['email'] = email
                session.permanent = True
                
                logging.info(f'User {email} ({user_id}) logged in successfully')
                return jsonify({'success': True}), 200
                
            except auth.InvalidIdTokenError:
                logging.error('Invalid ID token provided')
                return jsonify({'error': 'Invalid token'}), 401
            except auth.ExpiredIdTokenError:
                logging.error('Expired ID token provided')
                return jsonify({'error': 'Token expired'}), 401
            except auth.RevokedIdTokenError:
                logging.error('Revoked ID token provided')
                return jsonify({'error': 'Token revoked'}), 401
                
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401

    # GET request - show login page
    logging.info('Login page accessed')
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        logging.info(f'User {session.get("email", "unknown")} already logged in, redirecting to home')
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    logging.info(f'Home page accessed by user {session.get("email", "unknown")}')
    return render_template('home.html')

@app.route('/calculator')
@login_required
def calculator():
    logging.info(f'Calculator page accessed by user {session.get("email", "unknown")}')
    return render_template('calculator.html')

@app.route('/profile')
@login_required
def profile():
    logging.info(f'Profile page accessed by user {session.get("email", "unknown")}')
    return render_template('profile.html')

@app.route('/logout')
def logout():
    user_email = session.get('email', 'unknown')
    session.clear()
    logging.info(f'User {user_email} logged out')
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        logging.info(f"Prediction requested: {data}")
        print("Received data:", data)  # Debug log
        
        # Extract data from request
        destination = data.get('destination', '').lower()
        region = data.get('region', '').lower()
        days = int(data.get('days', 0))
        people = int(data.get('people', 0))
        travel_mode = data.get('travel_mode', '').lower()
        budget_level = data.get('budget_level', '').lower()
        
        # Validate inputs
        if not all([destination, days, people, travel_mode, budget_level]):
            print("Missing required fields:", {
                'destination': bool(destination),
                'days': bool(days),
                'people': bool(people),
                'travel_mode': bool(travel_mode),
                'budget_level': bool(budget_level)
            })
            return jsonify({
                'error': 'Missing required fields'
            }), 400
            
        if days < 1 or days > 30:
            return jsonify({
                'error': 'Number of days must be between 1 and 30'
            }), 400
            
        if people < 1 or people > 10:
            return jsonify({
                'error': 'Number of people must be between 1 and 10'
            }), 400
        
        # Make prediction
        try:
            predicted_costs = predictor.predict(
                destination=destination,
                region=region,
                days=days,
                people=people,
                travel_mode=travel_mode,
                budget_level=budget_level
            )
        except Exception as e:
            print(f"Error in prediction model: {e}")
            return jsonify({
                'error': 'Error calculating costs. Please try again.'
            }), 500
        
        print("Predicted costs:", predicted_costs)  # Debug log
        
        # Calculate total cost
        daily_total = sum(predicted_costs.values())  # Total cost per person per day
        total_cost = daily_total * days * people     # Total cost for all people for all days
        
        print("Daily total per person:", daily_total)  # Debug log
        print("Total cost for all:", total_cost)      # Debug log
        
        return jsonify({
            'predicted_costs': predicted_costs,        # Daily costs per person
            'daily_total': daily_total,               # Total daily cost per person
            'total_cost': total_cost                  # Total cost for all people and days
        })
        
    except ValueError as e:
        logging.error(f"Value error: {e}")
        print(f"Value error: {e}")
        return jsonify({
            'error': 'Invalid input values. Please check your inputs.'
        }), 400
    except Exception as e:
        logging.error(f"Error making prediction: {e}")
        print(f"Error making prediction: {e}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

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
    print("Loading trained model...")
    predictor = load_trained_model()
    print("Server starting! Access the travel calculator at: http://127.0.0.1:5000")
    app.run(debug=True) 