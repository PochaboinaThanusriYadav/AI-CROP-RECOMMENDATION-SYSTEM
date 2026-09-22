from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import requests
from crop_recommender import recommend_crops
from questionnaire_recommender import recommend_questionnaire

app = Flask(__name__)
CORS(app)

# -----------------------------
# Load model
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "mobilenetv2_soil.keras")
CLASS_PATH = os.path.join(BASE_DIR, "config", "soil_classes.json")

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as f:
    class_names = json.load(f)

print("MobileNetV2 model loaded successfully!")
print("Classes:", class_names)

# -----------------------------
# Soil image prediction
# -----------------------------
@app.route("/soil/analyze", methods=["POST"])
def analyze_soil():

    if "image" not in request.files:
        return jsonify({
            "error": "No image uploaded"
        }), 400

    file = request.files["image"]
    

    try:
        # Open image
        image = Image.open(file).convert("RGB")

        # Resize exactly as during training
        image = image.resize((224, 224))

        # Convert to NumPy
        image_array = np.array(image)

        # Normalize
        image_array = image_array.astype("float32") / 255.0

        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)

        # Prediction
        predictions = model.predict(image_array, verbose=0)

        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index])

        predicted_class = class_names[predicted_index]

        return jsonify({
            "soil_type": predicted_class,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# -----------------------------
# Health check
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Crop Recommendation Backend is running!"
    })

@app.route("/recommendation", methods=["POST"])
def recommendation():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No recommendation data provided"
        }), 400

    district = data.get("district")
    mandal = data.get("mandal")
    season = data.get("season", "Kharif")

    if not district:
        return jsonify({
            "error": "District is required"
        }), 400

    if not mandal:
        return jsonify({
            "error": "Mandal is required"
        }), 400

    recommendations = recommend_crops(
        district=district,
        mandal=mandal,
        season=season,
        top_n=5
    )

    if not recommendations:
        return jsonify({
            "error": "No historical crop data found for this location and season"
        }), 404

    primary = recommendations[0]

    alternatives = recommendations[1:]

    return jsonify({
        "recommended_crop": primary["crop"],
        "confidence": primary["cultivation_share"] / 100,
        "factors": [
            f"Historical cultivation share: {primary['cultivation_share']}%",
            f"Historical actual cultivated area: {primary['historical_actual_area']} acres",
            f"Location: {district}, {mandal}",
            f"Season: {season}"
        ],
        "alternatives": [
            item["crop"]
            for item in alternatives
        ],
        "recommendations": recommendations
    })


@app.route("/questionnaire/recommendation", methods=["POST"])
def questionnaire_recommendation():
    data = request.get_json() or {}
    try:
        recommendations = recommend_questionnaire(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not recommendations:
        return jsonify({"error": "No historical crop data found for this location and season"}), 404

    primary = recommendations[0]
    return jsonify({
        "recommended_crop": primary["crop"],
        "score": primary["score"],
        "confidence": round(primary["score"] / 100, 2),
        "factors": {
            "historical_location_score": primary["historical_score"],
            "irrigation_suitability": primary["irrigation_suitability"],
            "land_type_suitability": primary["land_type_suitability"],
            "season_suitability": primary["season_suitability"],
            "farmer_preference": primary["farmer_preference"],
        },
        "alternatives": [item["crop"] for item in recommendations[1:]],
        "recommendations": recommendations,
    })

@app.route("/weather", methods=["GET"])
def weather():
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({
            "error": "Latitude and longitude are required"
        }), 400

    try:
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 4,
            "timezone": "auto"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return jsonify(data)

    except requests.RequestException as e:
        return jsonify({
            "error": "Unable to fetch weather data",
            "details": str(e)
        }), 500

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
