# services.py

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import requests


def calculate_distance_between_addresses(address_one, address_two):
    geolocator = Nominatim(user_agent="ai_dashboard_chat_app")

    location_one = geolocator.geocode(address_one)
    location_two = geolocator.geocode(address_two)

    if not location_one or not location_two:
        return {
            "success": False,
            "message": "One or both addresses could not be found.",
        }

    point_one = (location_one.latitude, location_one.longitude)
    point_two = (location_two.latitude, location_two.longitude)

    distance_km = geodesic(point_one, point_two).km

    return {
        "success": True,
        "message": f"The straight-line distance between {location_one.address} and {location_two.address} is approximately {round(distance_km, 2)} km.",
    }


def ask_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={api_key}"
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, json=payload)
    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]
