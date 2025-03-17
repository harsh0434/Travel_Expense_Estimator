from django.shortcuts import render
from django.http import JsonResponse
import requests

# ✅ Add a home page view
def home(request):
    return render(request, "index.html")  # Ensure index.html exists

# ✅ Improved estimate function with error handling
def estimate(request):
    if request.method == "POST":
        destination = request.POST.get("destination", "")
        travel_mode = request.POST.get("travel_mode", "")
        num_people = request.POST.get("num_people", "")
        num_days = request.POST.get("num_days", "")

        payload = {
            "destination": destination,
            "travel_mode": travel_mode,
            "num_people": num_people,
            "num_days": num_days
        }

        response = requests.post("http://127.0.0.1:5000/estimate", json=payload)

        print("Response Status Code:", response.status_code)
        print("Response JSON:", response.text)  # Print full response

        if response.status_code == 200:
            estimated_cost = response.json().get("estimated_cost", "N/A")
            return render(request, "index.html", {
                "estimated_cost": estimated_cost,
                "destination": destination,
                "travel_mode": travel_mode,
                "num_people": num_people,
                "num_days": num_days
            })
        else:
            return render(request, "index.html", {
                "error": f"Error in estimation. Server responded with: {response.text}",
                "destination": destination,
                "travel_mode": travel_mode,
                "num_people": num_people,
                "num_days": num_days
            })

    return render(request, "index.html")