import os
import pickle
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse

# ✅ Set up the model path
MODEL_PATH = r"C:\Users\harsh\OneDrive\Desktop\Travel-Expense-Estimator\backend\models\travel_expense_model.pkl"

# ✅ Load the trained ML model (with error handling)
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as file:
        data = pickle.load(file)
        model = data["model"]
        label_encoders = data["label_encoders"]
else:
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

# ✅ Home page view
def home(request):
    return render(request, "index.html")  # Ensure index.html exists

# ✅ Function to predict expenses (UPDATED to handle unseen labels)
def predict_expense(destination, num_people, num_days, transport_mode):
    try:
        # Function to handle unseen labels
        def encode_with_fallback(label_encoder, value):
            if value in label_encoder.classes_:
                return label_encoder.transform([value])[0]
            else:
                return label_encoder.transform(["unknown"])[0]  # Assign to "unknown"

        # Convert categorical inputs using label encoders (handling unseen labels)
        destination_encoded = encode_with_fallback(label_encoders["destination"], destination)
        transport_mode_encoded = encode_with_fallback(label_encoders["transport_mode"], transport_mode)

        # Create DataFrame for prediction
        input_data = pd.DataFrame([[destination_encoded, num_people, num_days, transport_mode_encoded]],
                                  columns=["destination", "num_people", "num_days", "transport_mode"])

        # Predict estimated cost
        estimated_cost = model.predict(input_data)[0]
        return round(estimated_cost, 2)

    except Exception as e:
        return f"Error in prediction: {str(e)}"

# ✅ API View for estimating travel expenses
def estimate(request):
    if request.method == "POST":
        try:
            # Extract user inputs
            destination = request.POST.get("destination")
            num_people = int(request.POST.get("num_people"))
            num_days = int(request.POST.get("num_days"))
            transport_mode = request.POST.get("transport_mode")

            # Predict cost
            estimated_cost = predict_expense(destination, num_people, num_days, transport_mode)

            # Return JSON response
            return JsonResponse({"estimated_cost": estimated_cost})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
