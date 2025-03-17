import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend folder
CSV_PATH = os.path.join(BASE_DIR, "database", "travel_expense_dataset.csv")  # Correct CSV path
MODEL_PATH = os.path.join(BASE_DIR, "models", "travel_expense_model.pkl")  # Save model in 'models' folder
ENCODER_PATH = os.path.join(BASE_DIR, "models", "encoders.pkl")  # Save encoders in 'models' folder

# Load dataset
df = pd.read_csv(CSV_PATH)

# Encode categorical variables
le_dest = LabelEncoder()
le_travel = LabelEncoder()
le_accom = LabelEncoder()

df["destination_type"] = le_dest.fit_transform(df["destination_type"])
df["travel_mode"] = le_travel.fit_transform(df["travel_mode"])
df["accommodation"] = le_accom.fit_transform(df["accommodation"])

# Define features and target
X = df.drop(columns=["total_expense"])
y = df["total_expense"]

# Train a new model with the current scikit-learn version
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the new model and encoders
joblib.dump(model, MODEL_PATH)
joblib.dump({"dest": le_dest, "travel": le_travel, "accom": le_accom}, ENCODER_PATH)

print("✅ Model retrained and saved successfully at:", MODEL_PATH)
