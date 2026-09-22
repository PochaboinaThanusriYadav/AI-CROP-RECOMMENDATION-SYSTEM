from datetime import date


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _temperature_score(minimum, maximum):
    average = (minimum + maximum) / 2
    if 18 <= average <= 32:
        return 100, "Temperature is within the general planting range"
    if 15 <= average <= 35:
        return 70, "Temperature is near the general planting range"
    return 35, "Temperature is outside the general planting range"


def _rainfall_score(rainfall):
    if 0 <= rainfall <= 15:
        return 100, "Rainfall is light enough for planting activities"
    if rainfall <= 30:
        return 65, "Rainfall may affect field access"
    return 30, "Heavy rainfall may make field work unsuitable"


def _humidity_score(humidity):
    if 40 <= humidity <= 85:
        return 100, "Humidity is within a workable range"
    if 30 <= humidity <= 90:
        return 65, "Humidity is near the workable range"
    return 35, "Humidity is outside the workable range"


def _wind_score(wind):
    if wind <= 20:
        return 100, "Wind speed is low"
    if wind <= 35:
        return 65, "Wind speed may affect field activities"
    return 30, "Strong wind may make field activities unsuitable"


def _daily_advice(day, minimum, maximum, rainfall, humidity, wind):
    temperature_score, temperature_reason = _temperature_score(minimum, maximum)
    rainfall_score, rainfall_reason = _rainfall_score(rainfall)
    humidity_score, humidity_reason = _humidity_score(humidity)
    wind_score, wind_reason = _wind_score(wind)
    score = round(
        temperature_score * 0.30
        + rainfall_score * 0.30
        + humidity_score * 0.20
        + wind_score * 0.20
    )
    reasons = [temperature_reason, rainfall_reason, humidity_reason, wind_reason]
    return {
        "date": day,
        "score": score,
        "status": "Suitable" if score >= 70 else "Less suitable",
        "rainfall": rainfall,
        "temperature_min": minimum,
        "temperature_max": maximum,
        "humidity": humidity,
        "wind_speed": wind,
        "reasons": reasons,
    }


def advise_planting(crop, weather):
    daily = weather.get("daily") or {}
    dates = daily.get("time") or []
    maximums = daily.get("temperature_2m_max") or []
    minimums = daily.get("temperature_2m_min") or []
    rainfall = daily.get("precipitation_sum") or []
    current = weather.get("current") or {}
    current_humidity = _number(current.get("relative_humidity_2m"), 60)
    current_wind = _number(current.get("wind_speed_10m"), 10)

    days = []
    for index, day in enumerate(dates):
        minimum = _number(minimums[index] if index < len(minimums) else 20, 20)
        maximum = _number(maximums[index] if index < len(maximums) else 30, 30)
        rain = _number(rainfall[index] if index < len(rainfall) else 0, 0)
        days.append(_daily_advice(
            day,
            minimum,
            maximum,
            rain,
            current_humidity,
            current_wind,
        ))

    if not days:
        raise ValueError("Weather data does not contain a daily forecast")

    suitable_days = [item for item in days if item["score"] >= 70]
    average_score = round(sum(item["score"] for item in days) / len(days))
    if suitable_days:
        status = "Suitable"
        recommended_days = [item["date"] for item in suitable_days]
        first_day = suitable_days[0]["date"]
        reasons = suitable_days[0]["reasons"]
        window = "Today" if first_day == str(date.today()) else f"From {first_day}"
    else:
        status = "Less suitable"
        recommended_days = []
        window = "No suitable day in the next 4 days"
        reasons = ["No forecast day reached the suitability threshold"]

    return {
        "crop": crop,
        "planting_status": status,
        "score": average_score,
        "recommended_days": recommended_days,
        "recommended_window": window,
        "reasons": reasons,
        "daily_assessment": days,
        "method": "Generic weather suitability rules; not a crop-specific agronomic prediction",
    }