import json
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
import joblib
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import time
import traceback
import sys
import platform
import psutil
import warnings
warnings.filterwarnings('ignore')

# Configure logging with rotation
def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation (10MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        'logs/system_interactions.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_handler = RotatingFileHandler(
        'logs/performance_metrics.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    perf_handler.setFormatter(file_formatter)
    perf_logger.addHandler(perf_handler)
    
    # Create user interaction logger
    user_logger = logging.getLogger('user')
    user_handler = RotatingFileHandler(
        'logs/user_interactions.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    user_handler.setFormatter(file_formatter)
    user_logger.addHandler(user_handler)
    
    # Create error logger
    error_logger = logging.getLogger('error')
    error_handler = RotatingFileHandler(
        'logs/error_details.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_logger.addHandler(error_handler)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)
perf_logger = logging.getLogger('performance')
user_logger = logging.getLogger('user')
error_logger = logging.getLogger('error')

class TravelCostPredictor:
    def __init__(self):
        """Initialize the TravelCostPredictor with necessary components"""
        self.model = None
        self.scaler = StandardScaler()
        self.destination_encoder = LabelEncoder()
        self.region_encoder = LabelEncoder()
        self.travel_mode_encoder = LabelEncoder()
        self.budget_level_encoder = LabelEncoder()
        self.season_encoder = LabelEncoder()
        self.last_training_time = None
        self.model_accuracy = 0.0
        
        # Log system information
        self._log_system_info()
        
        # Initialize encoders with known values
        self.travel_mode_encoder.fit(['car', 'bus', 'train', 'flight'])
        self.budget_level_encoder.fit(['low', 'mid', 'high'])
        self.season_encoder.fit(['winter', 'summer', 'monsoon', 'autumn'])
        
        # Load data to initialize other encoders
        try:
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data['travel_data'])
                
                # Fit encoders with all possible values
                self.destination_encoder.fit(df['destination'].unique())
                self.region_encoder.fit(df['region'].unique())
            logger.info("Successfully initialized encoders with training data")
        except Exception as e:
            error_logger.error(f"Failed to initialize encoders: {str(e)}\n{traceback.format_exc()}")
            print(f"Warning: Could not initialize encoders with data: {str(e)}")

    def _log_system_info(self):
        """Log system information"""
        system_info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            'memory_available': f"{psutil.virtual_memory().available / (1024**3):.2f} GB"
        }
        logger.info(f"System Information: {system_info}")

    def _log_performance_metrics(self, operation, start_time, additional_info=None):
        """Log performance metrics for an operation"""
        duration = time.time() - start_time
        metrics = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat(),
            'memory_usage': f"{psutil.Process().memory_info().rss / (1024**2):.2f} MB"
        }
        if additional_info:
            metrics.update(additional_info)
        perf_logger.info(f"Performance Metrics: {metrics}")

    def _log_user_interaction(self, action, details):
        """Log user interactions"""
        user_logger.info(f"User Action: {action}, Details: {details}")

    def _log_error(self, error_type, error_message, traceback_info=None):
        """Log detailed error information"""
        error_details = {
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'system_state': {
                'memory_usage': f"{psutil.Process().memory_info().rss / (1024**2):.2f} MB",
                'cpu_percent': psutil.cpu_percent()
            }
        }
        if traceback_info:
            error_details['traceback'] = traceback_info
        error_logger.error(f"Error Details: {error_details}")

    def load_data(self):
        """Load and prepare training data with focus on cost patterns"""
        try:
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data['travel_data'])
            
            # Calculate cost metrics
            df['cost_per_person_day'] = df['total_cost'] / (df['days'] * df['people'])
            df['accommodation_per_day'] = df['accommodation_cost'] / df['days']
            df['food_per_person_day'] = df['food_cost'] / (df['days'] * df['people'])
            
            # Standardize budget levels
            budget_map = {
                'budget': 'low',
                'standard': 'mid',
                'luxury': 'high'
            }
            df['budget_level'] = df['budget_level'].map(budget_map)
            
            # Basic feature engineering
            df['season'] = df['month'].apply(self._get_season)
            df['is_peak_season'] = df['month'].apply(self._is_peak_season)
            df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
            
            # Calculate comfort score
            df['comfort_score'] = (df['accommodation_rating'] * 0.4 + 
                                 df['food_rating'] * 0.3 +
                                 df['activity_rating'] * 0.2 +
                                 df['transport_rating'] * 0.1)
            
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def _get_season(self, month):
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'summer'
        elif month in [6, 7, 8, 9]:
            return 'monsoon'
        else:
            return 'autumn'

    def _is_peak_season(self, month):
        peak_months = [12, 1, 5, 6, 7]
        return 1 if month in peak_months else 0

    def prepare_features(self, df, is_training=False):
        """Prepare features based on cost patterns"""
        try:
            # Core features
            core_features = [
                'days', 'people', 'budget_level', 'travel_mode',
                'destination', 'month', 'day_of_week'
            ]
            
            # Optional features with defaults
            optional_features = {
                'comfort_score': 4.0,
                'accommodation_rating': 4.0,
                'food_rating': 4.0
            }
            
            # Ensure core features are present
            missing_core = [f for f in core_features if f not in df.columns]
            if missing_core:
                raise ValueError(f"Missing required features: {', '.join(missing_core)}")
            
            # Add optional features with defaults
            for feature, default_value in optional_features.items():
                if feature not in df.columns:
                    df[feature] = default_value
            
            # Create basic derived features
            df['is_peak_season'] = df['month'].apply(self._is_peak_season)
            df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)
            
            # Create cost-related features
            df['base_accommodation_cost'] = df.apply(
                lambda x: self._get_base_accommodation_cost(x['budget_level'], x['destination']), 
                axis=1
            )
            
            # Encode categorical variables
            df['destination_encoded'] = self.destination_encoder.transform(df['destination'])
            df['travel_mode_encoded'] = self.travel_mode_encoder.transform(df['travel_mode'])
            df['budget_level_encoded'] = self.budget_level_encoder.transform(df['budget_level'])
            
            # Final feature selection
            feature_columns = [
                'days',
                'people',
                'base_accommodation_cost',
                'destination_encoded',
                'travel_mode_encoded',
                'budget_level_encoded',
                'is_peak_season',
                'is_weekend',
                'comfort_score'
            ]
            
            return df[feature_columns]
        except Exception as e:
            print(f"Error in feature preparation: {str(e)}")
            raise

    def _get_base_accommodation_cost(self, budget_level, destination):
        """Get base accommodation cost based on budget level and destination"""
        # Base costs per night for different budget levels
        base_costs = {
            'low': 1000,    # Budget hotels/hostels
            'mid': 3000,    # 3-star hotels
            'high': 8000    # 4/5-star hotels
        }
        
        # City multipliers
        city_multipliers = {
            'delhi': 1.2,
            'mumbai': 1.3,
            'bangalore': 1.2,
            'goa': 1.4,
            'kerala': 1.1,
            'ladakh': 1.5,
            'varanasi': 1.0
        }
        
        base_cost = base_costs.get(budget_level, base_costs['mid'])
        multiplier = city_multipliers.get(destination, 1.0)
        
        return base_cost * multiplier

    def _calculate_weather_score(self, temp, humidity, rainfall):
        """Calculate weather score based on comfort metrics"""
        # Temperature factor (20-30°C is ideal)
        temp_score = 1 - (temp - 25).abs() / 25
        
        # Humidity factor (40-60% is ideal)
        humidity_score = 1 - (humidity - 50).abs() / 50
        
        # Rainfall penalty
        rainfall_penalty = rainfall.apply(lambda x: 0.5 if x > 0 else 1)
        
        return (temp_score * 0.4 + humidity_score * 0.3 + rainfall_penalty * 0.3)

    def _get_default_value(self, feature):
        """Get default values for missing features"""
        defaults = {
            'accommodation_rating': 4.0,
            'food_rating': 4.0,
            'activity_rating': 4.0,
            'transport_rating': 4.0,
            'temperature': 25,
            'humidity': 60,
            'rainfall': 0
        }
        return defaults.get(feature, 0)

    def train(self):
        """Train a cost-pattern based model"""
        start_time = time.time()
        logger.info("Starting model training")
        print("Loading and preparing data...")
        
        try:
            df = self.load_data()
            if df is None or len(df) == 0:
                error_msg = "No training data available"
                self._log_error("DataError", error_msg)
                raise ValueError(error_msg)

            # Prepare features
            X = self.prepare_features(df, is_training=True)
            y = df['total_cost']

            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Scale the features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Create and train the model
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=4,
                min_samples_split=5,
                min_samples_leaf=3,
                subsample=0.8,
                loss='huber',
                alpha=0.9,
                random_state=42
            )

            # Perform cross-validation
            cv_scores = cross_val_score(
                self.model, 
                X_train_scaled, 
                y_train, 
                cv=5, 
                scoring='r2'
            )
            logger.info(f"Cross-validation R² scores: {cv_scores}")
            logger.info(f"Mean CV R² score: {np.mean(cv_scores):.3f} (+/- {np.std(cv_scores) * 2:.3f})")

            # Train the final model
            self.model.fit(X_train_scaled, y_train)

            # Make predictions
            y_pred = self.model.predict(X_test_scaled)

            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate accuracy as percentage of predictions within 10% of actual value
            within_10_percent = np.mean(np.abs(y_pred - y_test) / y_test <= 0.10) * 100
            within_20_percent = np.mean(np.abs(y_pred - y_test) / y_test <= 0.20) * 100

            # Log performance metrics
            self._log_performance_metrics(
                'model_training',
                start_time,
                {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2,
                    'within_10_percent': within_10_percent,
                    'within_20_percent': within_20_percent
                }
            )

            # Save model metrics
            self.model_accuracy = within_10_percent / 100
            self.last_training_time = datetime.now()

            # Save the model and scaler
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = os.path.join(model_dir, 'travel_cost_model.joblib')
            scaler_path = os.path.join(model_dir, 'scaler.joblib')
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Model and scaler saved successfully at {model_dir}")
            
        except Exception as e:
            self._log_error("TrainingError", str(e), traceback.format_exc())
            raise

    def update_model(self, new_data):
        """Update model with new data"""
        try:
            # Load existing data
            with open('data/travel_data.json', 'r') as f:
                existing_data = json.load(f)
            
            # Append new data
            existing_data['travel_data'].extend(new_data)
            
            # Save updated data
            with open('data/travel_data.json', 'w') as f:
                json.dump(existing_data, f, indent=4)
            
            # Retrain model
            self.train()
            
            print("Model updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating model: {e}")
            return False

    def get_destination_info(self, destination):
        """Get detailed information about a destination"""
        try:
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
                dest_data = next((entry for entry in data['travel_data'] if entry['destination'] == destination), None)
                
                if dest_data:
                    return {
                        'tourist_attractions': dest_data.get('tourist_attractions', []),
                        'local_food': dest_data.get('local_food', []),
                        'activities': dest_data.get('activities', []),
                        'best_time': self._get_best_time(dest_data['region']),
                        'weather': {
                            'temperature': dest_data['temperature'],
                            'humidity': dest_data['humidity'],
                            'rainfall': dest_data['rainfall']
                        },
                        'ratings': {
                            'accommodation': dest_data['accommodation_rating'],
                            'food': dest_data['food_rating'],
                            'activities': dest_data['activity_rating'],
                            'transport': dest_data['transport_rating']
                        }
                    }
                return None
        except Exception as e:
            print(f"Error getting destination info: {str(e)}")
            return None

    def _get_best_time(self, region):
        """Get best time to visit based on region"""
        best_times = {
            'north india': 'October to March (Winter)',
            'south india': 'November to February (Winter)',
            'east india': 'October to March (Winter)',
            'west india': 'November to February (Winter)'
        }
        return best_times.get(region, 'Winter season')

    def _save_prediction_history(self, prediction_data):
        """Save prediction history to a JSON file"""
        try:
            history_file = 'data/prediction_history.json'
            history = []
            
            # Load existing history if file exists
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            # Add timestamp to prediction data
            prediction_data['timestamp'] = datetime.now().isoformat()
            
            # Add new prediction to history
            history.append(prediction_data)
            
            # Keep only last 100 predictions
            if len(history) > 100:
                history = history[-100:]
                logger.info("Prediction history truncated to last 100 entries")
            
            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            logger.info("Prediction history saved successfully")
                
        except Exception as e:
            error_msg = f"Could not save prediction history: {str(e)}"
            logger.error(error_msg)
            print(f"Warning: {error_msg}")

    def predict(self, destination, region, days, people, travel_mode, budget_level):
        """Predict travel cost with proper feature scaling and log transformation"""
        start_time = time.time()
        try:
            # Log user interaction
            self._log_user_interaction(
                'prediction_request',
                {
                    'destination': destination,
                    'region': region,
                    'days': days,
                    'people': people,
                    'travel_mode': travel_mode,
                    'budget_level': budget_level
                }
            )
            
            # Input validation
            if not self._is_valid_indian_destination(destination):
                error_msg = f"Invalid destination: {destination}"
                self._log_error("ValidationError", error_msg)
                return None, error_msg
            
            if not region:
                region = self._get_region(destination)
                logger.info(f"Region not provided, using default region: {region}")
            
            budget_level = self._standardize_budget_level(budget_level)
            travel_mode = self._standardize_travel_mode(travel_mode)
            
            # Create a DataFrame with the input
            input_data = pd.DataFrame({
                'destination': [destination],
                'region': [region],
                'days': [days],
                'people': [people],
                'travel_mode': [travel_mode],
                'budget_level': [budget_level],
                'month': [datetime.now().month],
                'day_of_week': [datetime.now().strftime('%A')]
            })
            
            # Prepare features
            X = self.prepare_features(input_data, is_training=False)
            
            # Scale the features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            logger.info(f"Prediction made: {prediction}")
            
            # Log performance metrics
            self._log_performance_metrics(
                'prediction',
                start_time,
                {
                    'prediction_value': prediction,
                    'input_features': input_data.to_dict()
                }
            )
            
            # Save prediction history
            prediction_data = {
                'destination': destination,
                'region': region,
                'days': days,
                'people': people,
                'travel_mode': travel_mode,
                'budget_level': budget_level,
                'predicted_cost': float(prediction)
            }
            self._save_prediction_history(prediction_data)
            
            return prediction, None
            
        except Exception as e:
            self._log_error("PredictionError", str(e), traceback.format_exc())
            return None, f"Error making prediction: {str(e)}"

    def _calculate_confidence(self, input_data):
        """Calculate prediction confidence based on input parameters"""
        base_confidence = 0.85
        
        # Adjust confidence based on group size
        people = input_data['people']
        if 1 <= people <= 4:
            base_confidence += 0.05
        elif 5 <= people <= 8:
            base_confidence += 0.02
        else:
            base_confidence -= 0.03
            
        # Adjust confidence based on duration
        days = input_data['days']
        if 2 <= days <= 7:
            base_confidence += 0.05
        elif 8 <= days <= 14:
            base_confidence += 0.02
        else:
            base_confidence -= 0.03
            
        return min(max(base_confidence, 0.7), 0.95)

    def _is_valid_indian_destination(self, destination):
        """Check if the destination is a valid Indian location"""
        indian_regions = ['north india', 'south india', 'east india', 'west india']
        try:
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
                known_destinations = {entry['destination']: entry['region'] for entry in data['travel_data']}
                return destination in known_destinations and known_destinations[destination] in indian_regions
        except Exception:
            return False

    def _get_region(self, destination):
        """Get region based on destination"""
        try:
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
                destinations = {entry['destination']: entry['region'] for entry in data['travel_data']}
                return destinations.get(destination, 'north india')  # default to north india if not found
        except Exception as e:
            print(f"Error getting region: {e}")
            return 'north india'  # default region

    def _standardize_budget_level(self, budget_level):
        """Standardize budget level input"""
        budget_map = {
            'low': 'budget',
            'mid': 'standard',
            'high': 'luxury'
        }
        return budget_map.get(budget_level.lower(), 'standard')

    def _standardize_travel_mode(self, travel_mode):
        """Standardize travel mode input"""
        mode_map = {
            'airways': 'flight',
            'flight': 'flight',
            'train': 'train',
            'car': 'car',
            'bus': 'bus'
        }
        return mode_map.get(travel_mode.lower(), 'train')

def load_trained_model():
    """Load trained model and encoders"""
    try:
        model = joblib.load('models/travel_cost_model.joblib')
        encoders = joblib.load('models/encoders.joblib')
        return model, encoders
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

def format_currency(amount):
    """Format amount in Indian currency format"""
    try:
        amount = float(amount)
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.2f}"
    except:
        return "₹0.00"

if __name__ == "__main__":
    # Initialize the predictor
    model = TravelCostPredictor()
    
    # Train the model
    print("Training the model...")
    model.train()
    
    while True:
        try:
            # Get user input
            print("\n" + "-"*50)
            print("Available Indian destinations:")
            with open('data/travel_data.json', 'r') as f:
                data = json.load(f)
                destinations = sorted({entry['destination'] for entry in data['travel_data']})
                for i, dest in enumerate(destinations, 1):
                    print(f"{i}. {dest.title()}")
            
            print("\nEnter your travel details:")
            destination = input("Enter destination from the list above: ").lower()
            days = int(input("Enter number of days: "))
            people = int(input("Enter number of people: "))
            travel_mode = input("Enter travel mode (car/bus/train/flight): ").lower()
            budget_level = input("Enter budget level (low/mid/high): ").lower()
            
            # Validate input
            if days <= 0 or people <= 0:
                print("Days and number of people must be positive numbers.")
                continue
                
            # Standardize inputs
            budget_level = model._standardize_budget_level(budget_level)
            travel_mode = model._standardize_travel_mode(travel_mode)
            
            # Get region based on destination
            region = model._get_region(destination)
    
            # Make prediction
            result, confidence = model.predict(destination, region, days, people, travel_mode, budget_level)
            
            if result:
                print("\n" + "="*50)
                print(f"Travel Cost Prediction for {destination.title()}")
                print("="*50)
                
                # Cost Information
                print("\nCost Breakdown (Per Person Per Day):")
                print(f"- Accommodation: {format_currency(result * 0.4)}")
                print(f"- Food: {format_currency(result * 0.25)}")
                print(f"- Activities: {format_currency(result * 0.25)}")
                print(f"- Transport: {format_currency(result * 0.1)}")
                print(f"\nPer Person Per Day: {format_currency(result / (days * people))}")
                print(f"Total Trip Cost: {format_currency(result * days * people)}")
                print(f"Confidence Score: {confidence:.2%}")
                
                # Destination Information
                print("\nDestination Highlights:")
                print("\nMust-Visit Places:")
                for i, place in enumerate(model.get_destination_info(destination)['tourist_attractions'], 1):
                    print(f"{i}. {place}")
                
                print("\nLocal Delicacies:")
                for i, food in enumerate(model.get_destination_info(destination)['local_food'], 1):
                    print(f"{i}. {food}")
                
                print("\nRecommended Activities:")
                for i, activity in enumerate(model.get_destination_info(destination)['activities'], 1):
                    print(f"{i}. {activity}")
                
                print(f"\nBest Time to Visit: {model.get_destination_info(destination)['best_time']}")
                
                print("\nWeather Information:")
                print(f"Temperature: {model.get_destination_info(destination)['weather']['temperature']}°C")
                print(f"Humidity: {model.get_destination_info(destination)['weather']['humidity']}%")
                print(f"Rainfall: {'Yes' if model.get_destination_info(destination)['weather']['rainfall'] else 'No'}")
                
                # Ask if user wants to continue
                choice = input("\nWould you like to make another prediction? (yes/no): ").lower()
                if choice != 'yes':
                    break
            else:
                print("Failed to make prediction. Please check your input.")
                continue
                
        except ValueError as e:
            print("Please enter valid numbers for days and people.")
            continue
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continue 