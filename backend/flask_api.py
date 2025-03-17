from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/estimate", methods=["POST"])
def estimate_cost():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    try:
        destination = data.get("destination")
        travel_mode = data.get("travel_mode")
        num_people = int(data.get("num_people", 1))
        num_days = int(data.get("num_days", 1))

        # Simple cost estimation logic (modify as needed)
        cost_per_day = 1000 if travel_mode == "Flight" else 500
        estimated_cost = num_people * num_days * cost_per_day

        return jsonify({"estimated_cost": estimated_cost})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
