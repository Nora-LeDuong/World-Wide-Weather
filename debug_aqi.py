import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('OPENWEATHER_API_KEY')
city = ''

print(f"Testing AQI fetch for {city} with key starts with {api_key[:4]}...")

base_url_current = "http://api.openweathermap.org/data/2.5/weather"
params_current = {
    'q': city,
    'appid': api_key,
    'units': 'metric'
}
try:
    resp = requests.get(base_url_current, params=params_current, timeout=10)
    print(f"Weather Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        print(f"Lat: {lat}, Lon: {lon}")

        base_url_aqi = "http://api.openweathermap.org/data/2.5/air_pollution"
        params_aqi = {
            'lat': lat,
            'lon': lon,
            'appid': api_key
        }
        resp_aqi = requests.get(base_url_aqi, params=params_aqi, timeout=10)
        print(f"AQI Status: {resp_aqi.status_code}")
        print(f"AQI Response: {resp_aqi.text}")
    else:
        print(f"Weather Fetch Failed: {resp.text}")

except Exception as e:
    print(f"Exception: {e}")
