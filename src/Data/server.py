from flask import Flask, request, jsonify
import joblib
import numpy as np
import re

app = Flask(__name__)

# Load the model
model = joblib.load("income_model.pkl")

def parse_user_input(user_input):
    """
    Parse user input to extract the number of profiles and zipcode.
    """
    # Default values
    num_profiles = 100  # Default number of profiles
    zipcode = None  # Default zipcode (None means all zipcodes)

    # Extract number of profiles
    num_match = re.search(r"(\d+)\s*(?:customer|profile)", user_input, re.IGNORECASE)
    if num_match:
        num_profiles = int(num_match.group(1))

    # Extract zipcode
    zip_match = re.search(r"zipcode\s*(\d+)", user_input, re.IGNORECASE)
    if zip_match:
        zipcode = int(zip_match.group(1))

    return num_profiles, zipcode

@app.route("/generate", methods=["POST"])
def generate_profiles():
    # Get user input from the request
    data = request.json
    user_input = data.get("input", "").strip()

    # Check if the input is a valid generation command
    if not re.search(r"(generate|create|make)\s*\d*\s*(customer|profile)", user_input, re.IGNORECASE):
        return jsonify({"error": "Sorry, that's not a valid generation command. Please try again."})

    # Parse user input
    num_profiles, zipcode = parse_user_input(user_input)

    # Generate customer profiles
    try:
        synthetic_data = model.generate(num_profiles)

        # Filter by zipcode if specified
        if zipcode:
            synthetic_data = synthetic_data[synthetic_data["zipcode"] == zipcode]

        # Convert the DataFrame to a list of dictionaries
        results = synthetic_data.to_dict(orient="records")
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)