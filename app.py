from flask import Flask, render_template, request, session, jsonify, redirect
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from flask_session import Session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

API_KEY = "71cb48b82a248b0dfba8b7779ffb2c66"

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city_name)
    return (location.latitude, location.longitude) if location else (None, None)

def get_local_time(utc_timestamp, offset_seconds):
    return datetime.utcfromtimestamp(utc_timestamp + offset_seconds).strftime('%I:%M %p')

def get_background(condition, hour):
    condition = condition.lower()
    if "clear" in condition:
        return "GIFs/clear_day.gif" if hour < 18 else "GIFs/clear_night.gif"
    elif "cloud" in condition:
        return "GIFs/dark_clouds.gif"
    elif "light rain" in condition or "drizzle" in condition:
        return "GIFs/light_rain.gif"
    elif "thunder" in condition:
        return "GIFs/thunderstorm.gif"
    else:
        return "GIFs/clear_day.gif"

def fetch_weather_data(lat, lon, units):
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units={units}"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units={units}"

    current_res = requests.get(current_url)
    forecast_res = requests.get(forecast_url)

    if current_res.status_code == 200 and forecast_res.status_code == 200:
        current_data = current_res.json()
        forecast_data = forecast_res.json()
        timezone_offset = current_data.get("timezone", 0)
        rain_volume = current_data.get("rain", {}).get("1h", 0.0)
        pop = forecast_data["list"][0].get("pop", 0.0)

        weather_data = {
            "city": current_data["name"],
            "temperature": current_data["main"]["temp"],
            "description": current_data["weather"][0]["description"],
            "humidity": current_data["main"]["humidity"],
            "wind": current_data["wind"]["speed"],
            "real_feel": current_data["main"].get("feels_like"),
            "sunrise": get_local_time(current_data["sys"]["sunrise"], timezone_offset),
            "sunset": get_local_time(current_data["sys"]["sunset"], timezone_offset),
            "unit": "°C" if units == "metric" else "°F",
            "rain": f"{rain_volume} mm" if rain_volume > 0 else "No rain",
            "pop": int(pop * 100),
            "pressure": current_data["main"]["pressure"],
            "uv": 8,
            "aqi": 135,
            "hourly": [
                {
                    "temp": item["main"]["temp"],
                    "wind": item["wind"]["speed"],
                    "time": datetime.utcfromtimestamp(item["dt"] + timezone_offset).strftime("%H:00"),
                    "icon": item["weather"][0]["icon"]
                } for item in forecast_data["list"][:6]
            ]
        }
        return weather_data
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    background_gif = "GIFs/clear_day.gif"
    selected_unit = session.get("unit", "metric")
    theme = session.get("theme", "light")
    favorites = session.get("favorites", [])

    if request.method == "POST":
        if "city" in request.form:
            city = request.form["city"]
            units = request.form.get("units", selected_unit)
            lat, lon = get_coordinates(city)
            if lat and lon:
                weather_data = fetch_weather_data(lat, lon, units)
                if weather_data:
                    hour = datetime.utcnow().hour + int((datetime.utcnow().timestamp() - datetime.now().timestamp()) / 3600)
                    background_gif = get_background(weather_data["description"], hour)
                    session["unit"] = units

        elif "unit_toggle" in request.form:
            session["unit"] = request.form["unit_toggle"]

        elif "theme_toggle" in request.form:
            session["theme"] = request.form["theme_toggle"]

        elif "add_favorite" in request.form:
            city = request.form["add_favorite"]
            if city and city not in favorites:
                favorites.append(city)
                session["favorites"] = favorites

        elif "remove_favorite" in request.form:
            city = request.form["remove_favorite"]
            if city in favorites:
                favorites.remove(city)
                session["favorites"] = favorites

    return render_template(
        "index.html",
        weather=weather_data,
        gif=background_gif,
        theme=theme,
        selected_unit=session.get("unit", "metric"),
        favorites=session.get("favorites", [])
    )

@app.route("/weather_by_coords", methods=["POST"])
def weather_by_coords():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    units = session.get("unit", "metric")
    if lat and lon:
        weather_data = fetch_weather_data(lat, lon, units)
        if weather_data:
            session["temp_weather"] = weather_data
            hour = datetime.utcnow().hour + int((datetime.utcnow().timestamp() - datetime.now().timestamp()) / 3600)
            session["temp_gif"] = get_background(weather_data["description"], hour)
            return jsonify({"success": True})
    return jsonify({"error": "Coordinates missing"}), 400

@app.route("/set_temp_weather")
def set_temp_weather():
    return render_template(
        "index.html",
        weather=session.get("temp_weather"),
        gif=session.get("temp_gif", "GIFs/clear_day.gif"),
        theme=session.get("theme", "light"),
        selected_unit=session.get("unit", "metric"),
        favorites=session.get("favorites", [])
    )

@app.route("/favorites", methods=["GET", "POST"])
def favorites_page():
    unit = session.get("unit", "metric")
    favorites = session.get("favorites", [])

    if request.method == "POST":
        if "remove_favorite" in request.form:
            city = request.form["remove_favorite"]
            if city in favorites:
                favorites.remove(city)
                session["favorites"] = favorites

    favorite_weather_data = []
    for city in favorites:
        lat, lon = get_coordinates(city)
        if lat and lon:
            data = fetch_weather_data(lat, lon, unit)
            if data:
                favorite_weather_data.append({
                    "city": city.title(),
                    "temperature": data["temperature"],
                    "description": data["description"],
                    "unit": "°C" if unit == "metric" else "°F"
                })

    return render_template("favorites.html", favorites=favorite_weather_data, theme=session.get("theme", "light"))

if __name__ == "__main__":
    app.run(debug=True)
