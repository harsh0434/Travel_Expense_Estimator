import pandas as pd

# Define sample data
data = {
    "destination_type": ["beach", "mountain", "city", "desert"],
    "travel_mode": ["flight", "train", "bus", "car"],
    "accommodation": ["hotel", "hostel", "apartment", "hotel"],
    "num_people": [2, 3, 4, 2],
    "num_days": [5, 7, 4, 3],
    "total_expense": [5000, 7000, 4000, 3000],
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save as CSV
csv_path = "database/travel_expense_dataset.csv"  # ✅ Corrected path
df.to_csv(csv_path, index=False)

print(f"✅ CSV file created successfully at {csv_path}")
