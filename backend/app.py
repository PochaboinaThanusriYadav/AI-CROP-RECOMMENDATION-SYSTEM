from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import requests
from crop_recommender import recommend_crops
from questionnaire_recommender import questionnaire_recommendation
from planting_advisor import advise_planting

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

SOIL_CROP_MAP = {
    "Alluvial_Soil": ["Paddy", "Wheat", "Maize", "Sugarcane"],
    "Black_Soil": ["Cotton", "Soyabean", "Jowar", "Sunflower"],
    "Red_Soil": ["Groundnut", "Red Gram", "Green Gram", "Millets"],
    "Laterite_Soil": ["Cashew", "Coconut", "Groundnut", "Pineapple"],
    "Arid_Soil": ["Bajra", "Jowar", "Millets", "Groundnut"],
    "Mountain_Soil": ["Maize", "Potato", "Vegetables", "Pulses"],
    "Yellow_Soil": ["Groundnut", "Maize", "Pulses", "Millets"],
}

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
        recommended_crops = SOIL_CROP_MAP.get(predicted_class, [])

        return jsonify({
            "soil_type": predicted_class,
            "confidence": confidence,
            "recommended_crops": recommended_crops,
            "message": "These are preliminary crop suggestions based on the detected soil type.",
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
        "score": primary["cultivation_share"],
        "historical_cultivation_share": primary["cultivation_share"],
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
def questionnaire_recommendation_api():
    data = request.get_json() or {}
    required_fields = ["district", "mandal", "season", "land_type", "irrigation"]
    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing,
        }), 400

    try:
        result = questionnaire_recommendation(
            district=data["district"],
            mandal=data["mandal"],
            season=data["season"],
            land_type=data["land_type"],
            irrigation=data["irrigation"],
            water_source=data.get("water_source"),
            previous_crop=data.get("previous_crop"),
            land_area=data.get("land_area"),
            crop_duration=data.get("crop_duration"),
            top_n=5,
        )
        if result is None:
            return jsonify({
                "error": "No suitable crop data found for the given location and season."
            }), 404
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 500

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


@app.route("/planting-advisory", methods=["POST"])
def planting_advisory():
    data = request.get_json() or {}
    crop = data.get("crop")
    weather_data = data.get("weather")

    if not crop or not isinstance(weather_data, dict):
        return jsonify({
            "error": "Crop and weather data are required"
        }), 400

    try:
        return jsonify(advise_planting(crop, weather_data))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
