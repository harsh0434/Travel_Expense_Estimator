import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression

# Load the dataset
df = pd.read_csv(r"C:\Users\harsh\OneDrive\Desktop\Travel-Expense-Estimator\backend\database\travel_expenses.csv")

# Encode categorical columns
label_encoders = {}

for col in ["destination", "transport_mode"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

    # Ensure the label encoder can handle unknown values
    le.classes_ = np.append(le.classes_, "unknown")

    label_encoders[col] = le  # Store label encoders for future use

# Define features and target variable
X = df.drop(columns=["estimated_cost"])  # Independent variables
y = df["estimated_cost"]  # Dependent variable

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Save model and label encoders
with open("travel_expense_model.pkl", "wb") as file:
    pickle.dump({"model": model, "label_encoders": label_encoders}, file)

print("Model trained and saved successfully as travel_expense_model.pkl")
