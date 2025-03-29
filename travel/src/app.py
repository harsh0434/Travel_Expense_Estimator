from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from predict import load_trained_model
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
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
        predicted_costs = predictor.predict(
            destination=destination,
            region=region,
            days=days,
            people=people,
            travel_mode=travel_mode,
            budget_level=budget_level
        )
        
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
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("Loading trained model...")
    predictor = load_trained_model()
    print("Server starting! Access the travel calculator at: http://127.0.0.1:5000")
    app.run(debug=True) 