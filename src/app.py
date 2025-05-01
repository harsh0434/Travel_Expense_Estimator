from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, make_response, session
from predict import load_trained_model
import os
import logging
from datetime import timedelta

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)  # Required for session
app.permanent_session_lifetime = timedelta(days=7)  # Session lasts 7 days

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    logging.info('Login page accessed')
    return render_template('login.html')

@app.route('/home')
def home():
    logging.info('Home page accessed')
    return render_template('home.html')

@app.route('/calculator')
def calculator():
    logging.info('Calculator page accessed')
    return render_template('calculator.html')

@app.route('/profile')
def profile():
    logging.info('Profile page accessed')
    return render_template('profile.html')

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