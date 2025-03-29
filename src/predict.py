import json
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

class TravelCostPredictor:
    def __init__(self):
        self.model = None
        self.destination_encoder = LabelEncoder()
        self.region_encoder = LabelEncoder()
        self.travel_mode_encoder = LabelEncoder()
        self.budget_level_encoder = LabelEncoder()
        
        # Add destination to region mapping
        self.destination_to_region = {
            'delhi': 'north india',
            'agra': 'north india',
            'jaipur': 'north india',
            'amritsar': 'north india',
            'shimla': 'north india',
            'manali': 'north india',
            'rishikesh': 'north india',
            'ladakh': 'north india',
            
            'mumbai': 'west india',
            'goa': 'west india',
            'udaipur': 'west india',
            'pushkar': 'west india',
            'kutch': 'west india',
            
            'kerala': 'south india',
            'bangalore': 'south india',
            'hyderabad': 'south india',
            'chennai': 'south india',
            'hampi': 'south india',
            'mysore': 'south india',
            'ooty': 'south india',
            'munnar': 'south india',
            'coorg': 'south india',
            
            'kolkata': 'east india',
            'varanasi': 'east india',
            'darjeeling': 'east india',
            'khajuraho': 'central india',
            'ranthambore': 'central india',
            
            'kaziranga': 'northeast india',
            'andaman': 'east india'
        }
        
        self.base_costs = {
            'low': {
                'accommodation': 800,   # Budget hotels/hostels
                'food': 400,           # Local restaurants/street food
                'activities': 300,     # Basic sightseeing
                'transport': {
                    'car': 600,
                    'bus': 300,
                    'train': 400,
                    'airways': 1500
                }
            },
            'mid': {
                'accommodation': 2000,  # 3-star hotels
                'food': 800,           # Mix of restaurants
                'activities': 600,     # Tours and activities
                'transport': {
                    'car': 1200,
                    'bus': 500,
                    'train': 800,
                    'airways': 2500
                }
            },
            'high': {
                'accommodation': 4000,  # 4-5 star hotels
                'food': 1500,          # High-end restaurants
                'activities': 1200,    # Premium experiences
                'transport': {
                    'car': 2000,
                    'bus': 800,
                    'train': 1500,
                    'airways': 4000
                }
            }
        }
        
        self.region_multipliers = {
            'north india': 1.1,
            'south india': 1.1,
            'east india': 1.0,
            'west india': 1.2,
            'central india': 1.0,
            'northeast india': 1.2
        }

    def load_data(self):
        """Load training data from JSON file"""
        try:
            with open('data/travel_costs.json', 'r') as f:
                data = json.load(f)
                return data['historical_costs']
        except Exception as e:
            print(f"Error loading training data: {e}")
            return None

    def prepare_features(self, data):
        """Prepare features for model training"""
        if not data:
            return None, None
            
        # Fit label encoders
        destinations = [d['destination'] for d in data]
        regions = [d['region'] for d in data]
        travel_modes = [d['travel_mode'] for d in data]
        budget_levels = [d['budget_level'] for d in data]
        
        self.destination_encoder.fit(destinations)
        self.region_encoder.fit(regions)
        self.travel_mode_encoder.fit(travel_modes)
        self.budget_level_encoder.fit(budget_levels)
        
        # Transform features
        X = np.array([
            [
                self.destination_encoder.transform([d['destination']])[0],
                self.region_encoder.transform([d['region']])[0],
                d['days'],
                d['people'],
                self.travel_mode_encoder.transform([d['travel_mode']])[0],
                self.budget_level_encoder.transform([d['budget_level']])[0]
            ] for d in data
        ])
        
        y = np.array([d['total_cost_per_person_per_day'] for d in data])
        return X, y

    def train(self):
        """Train the model"""
        print("Training model...")
        data = self.load_data()
        if not data:
            print("Using base costs for predictions")
            return
            
        X, y = self.prepare_features(data)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save the model and encoders
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/travel_cost_model.joblib')
        joblib.dump({
            'destination': self.destination_encoder,
            'region': self.region_encoder,
            'travel_mode': self.travel_mode_encoder,
            'budget_level': self.budget_level_encoder
        }, 'models/encoders.joblib')
        print("Model trained and saved successfully!")

    def calculate_base_costs(self, budget_level, travel_mode):
        """Calculate base costs based on budget level"""
        base = self.base_costs[budget_level]
        return {
            'accommodation': base['accommodation'],
            'food': base['food'],
            'activities': base['activities'],
            'transport': base['transport'][travel_mode]
        }

    def predict(self, destination, region=None, days=1, people=1, travel_mode='train', budget_level='mid'):
        """Make a prediction"""
        try:
            # Get region from destination if not provided
            if not region:
                region = self.destination_to_region.get(destination.lower(), 'north india')
            
            # Validate inputs
            if budget_level not in self.base_costs:
                raise ValueError(f"Invalid budget level: {budget_level}")
            
            if travel_mode not in self.base_costs['low']['transport']:
                raise ValueError(f"Invalid travel mode: {travel_mode}")
            
            # Calculate base costs
            base_costs = self.calculate_base_costs(budget_level, travel_mode)
            
            # Apply region multiplier
            region_multiplier = self.region_multipliers.get(region.lower(), 1.0)
            
            # Calculate destination multiplier
            destination_multipliers = {
                'goa': 1.3,
                'kerala': 1.2,
                'ladakh': 1.3,
                'agra': 1.1,
                'varanasi': 1.0,
                'manali': 1.2,
                'ooty': 1.1,
                'mumbai': 1.3,
                'delhi': 1.2,
                'bangalore': 1.2,
                'kolkata': 1.1,
                'chennai': 1.1,
                'hyderabad': 1.1,
                'jaipur': 1.1,
                'shimla': 1.2,
                'darjeeling': 1.2,
                'mysore': 1.0,
                'udaipur': 1.2,
                'rishikesh': 1.1,
                'amritsar': 1.1,
                'andaman': 1.4,
                'hampi': 1.1,
                'khajuraho': 1.2,
                'pushkar': 1.1,
                'ranthambore': 1.2,
                'munnar': 1.2,
                'mahabaleshwar': 1.1,
                'kutch': 1.2,
                'coorg': 1.2,
                'kaziranga': 1.3
            }
            destination_multiplier = destination_multipliers.get(destination.lower(), 1.0)
            
            # Calculate final costs with all multipliers
            predicted_costs = {
                'accommodation': int(base_costs['accommodation'] * region_multiplier * destination_multiplier),
                'food': int(base_costs['food'] * region_multiplier * destination_multiplier),
                'activities': int(base_costs['activities'] * region_multiplier * destination_multiplier),
                'transport': int(base_costs['transport'] * region_multiplier * destination_multiplier)
            }
            
            return predicted_costs
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            raise

def load_trained_model():
    """Load or create a new predictor"""
    print("Loading trained model...")
    predictor = TravelCostPredictor()
    predictor.train()
    return predictor

if __name__ == "__main__":
    # Load or train the model
    predictor = load_trained_model()
    
    # Get user input
    print("\nTravel Cost Predictor")
    print("--------------------")
    destination = input("Enter destination: ").lower()
    days = int(input("Enter number of days: "))
    people = int(input("Enter number of people: "))
    travel_mode = input("Enter travel mode (car/bus/train/airways): ").lower()
    budget_level = input("Enter budget level (low/mid/high): ").lower()
    
    # Get region from destination
    with open('data/travel_costs.json', 'r') as f:
        data = json.load(f)
        destinations = {entry['destination']: entry['region'] for entry in data['historical_costs']}
        region = destinations.get(destination, 'north india')  # default to north india if not found
    
    # Make prediction
    predicted_costs = predictor.predict(destination, region, days, people, travel_mode, budget_level)
    
    # Calculate total cost
    daily_total = sum(predicted_costs.values())
    total_cost = daily_total * days * people
    
    # Display results
    print("\nEstimated Costs (per person per day):")
    print(f"Accommodation: ₹{predicted_costs['accommodation']:,}")
    print(f"Food: ₹{predicted_costs['food']:,}")
    print(f"Activities: ₹{predicted_costs['activities']:,}")
    print(f"Transportation: ₹{predicted_costs['transport']:,}")
    print(f"\nTotal cost for {people} people for {days} days: ₹{total_cost:,}") 