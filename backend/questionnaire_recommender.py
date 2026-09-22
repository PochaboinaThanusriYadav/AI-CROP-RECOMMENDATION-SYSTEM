import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(BASE_DIR, "data", "crop_location_profile.csv")
profile = pd.read_csv(PROFILE_FILE).fillna("")

for column in ["district", "mandal", "season", "crop"]:
    profile[column] = profile[column].astype(str).str.strip()


def _text(value):
    return str(value or "").strip().lower()


def _matches(crop, names):
    crop_name = _text(crop)
    return any(name in crop_name for name in names)


def _irrigation_score(crop, irrigation, water):
    water_level = _text(water)
    irrigated = _text(irrigation) == "irrigated"
    water_score = {"low": 45, "medium": 75, "high": 100}.get(water_level, 60)

    water_intensive = ["paddy", "rice", "sugarcane", "turmeric", "banana"]
    drought_tolerant = [
        "cotton", "red gram", "pigeon", "green gram", "black gram",
        "bengalgram", "chickpea", "sorghum", "jowar", "millet",
        "groundnut", "sesame",
    ]

    if _matches(crop, water_intensive):
        return min(100, water_score + (15 if irrigated else -15))
    if _matches(crop, drought_tolerant):
        return min(100, water_score + (10 if not irrigated else 0))
    return min(100, water_score + (5 if irrigated else 0))


def _land_score(crop, land_type):
    land = _text(land_type)
    if not land:
        return 60
    clay_crops = ["paddy", "rice", "sugarcane", "turmeric"]
    sandy_crops = ["groundnut", "cotton", "millet", "sesame", "green gram"]
    loamy_crops = ["maize", "cotton", "red gram", "pigeon", "chickpea", "vegetable"]

    if "clay" in land or "black" in land:
        return 90 if _matches(crop, clay_crops) else 65
    if "sandy" in land:
        return 90 if _matches(crop, sandy_crops) else 65
    if "loam" in land or "red" in land:
        return 90 if _matches(crop, loamy_crops) else 70
    return 70


def _season_score(crop, season):
    season_name = _text(season)
    if season_name == "kharif":
        return 95 if _matches(crop, ["paddy", "cotton", "maize", "red gram", "groundnut", "soybean"]) else 75
    if season_name == "rabi":
        return 95 if _matches(crop, ["wheat", "chickpea", "bengalgram", "green gram", "black gram", "maize"]) else 75
    return 60


def _preference_score(crop, previous_crop, duration):
    previous = _text(previous_crop)
    duration_name = _text(duration)
    score = 70
    if previous and previous not in _text(crop):
        score += 10
    if duration_name == "short" and _matches(crop, ["green gram", "black gram", "sesame", "millet"]):
        score += 20
    elif duration_name == "long" and _matches(crop, ["paddy", "sugarcane", "turmeric", "cotton"]):
        score += 20
    return min(100, score)


def recommend_questionnaire(data, top_n=5):
    district = str(data.get("district", "")).strip()
    mandal = str(data.get("mandal", "")).strip()
    season = str(data.get("season", "")).strip()
    if not district or not mandal or not season:
        raise ValueError("District, mandal and season are required")

    location = profile[
        (profile["district"].str.lower() == district.lower())
        & (profile["mandal"].str.lower() == mandal.lower())
        & (profile["season"].str.lower() == season.lower())
    ].copy()
    scope = "mandal"
    if location.empty:
        location = profile[
            (profile["district"].str.lower() == district.lower())
            & (profile["season"].str.lower() == season.lower())
        ].copy()
        scope = "district"
    if location.empty:
        return []

    location = location[~location["crop"].str.lower().isin(["gross areas", "total"])].copy()
    total_share = location["cultivation_share"].astype(float).sum()
    if total_share <= 0:
        return []

    land_type = data.get("land_type") or data.get("soil_type")
    duration = data.get("crop_duration") or data.get("duration")
    recommendations = []
    for _, row in location.iterrows():
        historical = float(row["cultivation_share"]) / float(total_share) * 100
        irrigation = _irrigation_score(row["crop"], data.get("irrigation"), data.get("water"))
        land = _land_score(row["crop"], land_type)
        season_score = _season_score(row["crop"], season)
        preference = _preference_score(row["crop"], data.get("previous_crop"), duration)
        score = (historical * 0.50) + (irrigation * 0.20) + (land * 0.15) + (season_score * 0.10) + (preference * 0.05)
        recommendations.append({
            "crop": row["crop"],
            "score": float(round(score, 2)),
            "historical_score": float(round(historical, 2)),
            "irrigation_suitability": irrigation,
            "land_type_suitability": land,
            "season_suitability": season_score,
            "farmer_preference": preference,
            "historical_actual_area": float(round(float(row["total_actual_area"]), 2)),
            "records": int(row["records"]),
        })

    return sorted(recommendations, key=lambda item: item["score"], reverse=True)[:top_n]