import csv

# Define the data
data = [
    ["destination", "num_people", "num_days", "transport_mode", "estimated_cost"],
    ["Goa", 2, 5, "Flight", 15000],
    ["Mumbai", 3, 4, "Train", 7000],
    ["Delhi", 1, 3, "Bus", 3500],
    ["Bangalore", 4, 6, "Flight", 18000],
    ["Chennai", 2, 3, "Train", 8000],
    ["Kolkata", 5, 7, "Bus", 6000],
    ["Hyderabad", 3, 5, "Flight", 12000],
    ["Jaipur", 2, 4, "Bus", 5000],
    ["Pune", 1, 2, "Train", 4000],
    ["Manali", 3, 6, "Bus", 9500],
    ["Shimla", 2, 5, "Train", 8500],
    ["Ooty", 4, 4, "Flight", 16000],
    ["Kerala", 5, 7, "Flight", 22000],
    ["Ahmedabad", 3, 5, "Bus", 7800],
    ["Varanasi", 2, 3, "Train", 5000],
    ["Ladakh", 2, 6, "Flight", 25000]
]

# Create and save the CSV file
with open("travel_expenses.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)

print("CSV file 'travel_expenses.csv' created successfully!")
