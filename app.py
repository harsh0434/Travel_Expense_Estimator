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