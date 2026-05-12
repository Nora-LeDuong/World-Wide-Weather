import requests
from flask import current_app
from datetime import datetime
import json
import traceback
import unicodedata

CITY_NAME_MAPPINGS = {
    'sa pa': 'Sa Pa',
    'đà lạt': 'Đà Lạt',
    'dalat': 'Đà Lạt',
}

VIETNAMESE_CITIES = {'sa pa', 'đà lạt'}

def get_display_city_name(api_city_name, lang='en'):
    if lang == 'vi':
        lookup_key = api_city_name.lower().strip()
        return CITY_NAME_MAPPINGS.get(lookup_key, api_city_name)
    return api_city_name

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def get_weather_data(city_name, lang='en'):

    api_key = current_app.config['OPENWEATHER_API_KEY']
    print(f"Using API Key: {api_key}")
    
    try:
        # 1. Get Current Weather (to get lat/lon and current state)
        base_url_current = "http://api.openweathermap.org/data/2.5/weather"
        
        city_query = city_name.strip()
        
        params_current = {
            'q': city_query,
            'appid': api_key,
            'units': 'metric',
            'lang': lang
        }
        
        # Retry Strategy
        variations = []
        
        # Special handling for "sapa" -> prioritize "Sa Pa, VN" to avoid "Sapa-Sapa, PH"
        if city_query.lower() in ['sapa', 'sa pa']:
             variations.append("Sa Pa, VN")
             variations.append("Sapa, VN")

        
        # 1. Original
        variations.append(city_query)
        
        # 2. Original + ", VN" (if not already there)
        if ", vn" not in city_query.lower():
             variations.append(f"{city_query}, VN")
             
        # 3. Normalized
        normalized = remove_accents(city_query)
        if normalized != city_query:
            variations.append(normalized)
            
        # 4. Normalized + ", VN"
        if ", vn" not in normalized.lower() and normalized != city_query:
            variations.append(f"{normalized}, VN")
            
        print(f"Search variations: {variations}")
        
        response_current = None
        for variant in variations:
             print(f"Trying: {variant}")
             params_current['q'] = variant
             try:
                response_current = requests.get(base_url_current, params=params_current, timeout=10)
                if response_current.status_code == 200:
                    print(f"Found match with: {variant}")
                    break
             except Exception:
                 continue
        
        if not response_current:
             return {'error': f"Unable to fetch data for '{city_name}' (Network Error)"}

        if response_current.status_code != 200:
            return {'error': f"Không tìm thấy thành phố '{city_name}' hoặc lỗi API ({response_current.status_code})"}
            
        current_data = response_current.json()
        
        # Extract Coordinates
        lat = current_data['coord']['lat']
        lon = current_data['coord']['lon']
        
        # Process Current Data
        final_current = _process_current_data(current_data, lang)
        
        # 1. Get Air Pollution (AQI)
        aqi_val = None
        base_url_aqi = "http://api.openweathermap.org/data/2.5/air_pollution"
        params_aqi = {
            'lat': lat,
            'lon': lon,
            'appid': api_key
        }
        try:
             resp_aqi = requests.get(base_url_aqi, params=params_aqi, timeout=5)
             if resp_aqi.status_code == 200:
                 aqi_data = resp_aqi.json()
                 if aqi_data.get('list'):
                     aqi_val = aqi_data['list'][0]['main']['aqi'] # 1=Good, 5=Poor
        except Exception as e_aqi:
            pass
        
        final_current['aqi'] = aqi_val

        # 2. Get Forecast
        forecast_result = []
        hourly_result = [] # New hourly forecast
        
        # Try 5 Day Forecast first
        base_url_forecast = "http://api.openweathermap.org/data/2.5/forecast"
        params_forecast = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'lang': lang
        }
        
        print(f"Requesting Forecast: {base_url_forecast}")
        response_forecast = requests.get(base_url_forecast, params=params_forecast, timeout=10)
        
        if response_forecast.status_code == 200:
            print("Forecast 5-day: Success")
            f_data = response_forecast.json()
            forecast_result = _process_forecast_data(f_data)
            hourly_result = _process_hourly_data(f_data) # Extract next 24h
        else:
            print(f"Forecast 5-day Status: {response_forecast.status_code}")
            base_url_onecall = "https://api.openweathermap.org/data/3.0/onecall"
            params_onecall = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': lang,
                'exclude': 'minutely,alerts'
            }
            response_onecall = requests.get(base_url_onecall, params=params_onecall, timeout=10)
            if response_onecall.status_code == 200:
                print("OneCall: Success")
                onecall_data = response_onecall.json()
                forecast_result = _process_onecall_daily(onecall_data['daily'], lang)
                if 'hourly' in onecall_data:
                    hourly_result = _process_onecall_hourly(onecall_data['hourly'])

        rain_prob = 0
        if forecast_result and len(forecast_result) > 0:
            rain_prob = forecast_result[0].get('rain_prob', 0)

        current_icon_code = final_current['icon']
        if current_icon_code[:2] in ['09', '10', '11', '13']:
            rain_prob = max(rain_prob, 90)

        print(f"DEBUG: Extracted rain_prob: {rain_prob} (Type: {type(rain_prob)})")
        final_current['rain_prob'] = int(rain_prob) if rain_prob is not None else 0
        final_current['wind_speed'] = round(final_current['wind_speed'], 1) # Round wind speed

        # Sync rain_prob with the first day of forecast (Today) to ensure consistency
        if forecast_result and len(forecast_result) > 0:
            # Check if dates match to be safe
            forecast_result[0]['rain_prob'] = max(forecast_result[0]['rain_prob'], final_current['rain_prob'])

        return {
            'current': final_current,
            'forecast': forecast_result,
            'hourly': hourly_result,
            'lang': lang,
            'error': None
        }

    except Exception as e:
        traceback.print_exc()
        return {'error': 'Lỗi kết nối đến dịch vụ thời tiết.'}

def _process_current_data(data, lang='en'):
    # Sunrise/Sunset
    sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
    sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
    
    return {
        'city': get_display_city_name(data['name'], lang),
        'country': data['sys']['country'],
        'country_code_lower': data['sys']['country'].lower(),
        'temp': round(data['main']['temp']),
        'feels_like': round(data['main']['feels_like']),
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'], # hPa
        'visibility': data.get('visibility', 0) / 1000, # Convert to km
        'sunrise': sunrise,
        'sunset': sunset,
        'wind_speed': data['wind']['speed'],
        'description': data['weather'][0]['description'].capitalize(),
        'icon': data['weather'][0]['icon'],
        'icon_url': None, 
        'dt': datetime.fromtimestamp(data['dt']),
        'bg_class': _get_bg_class(data['weather'][0]['icon'])
    }

def _get_bg_class(icon_code):
    if not icon_code:
        return 'bg-default'
    
    # Day/Night suffix
    is_day = 'd' in icon_code
    
    # Codes: https://openweathermap.org/weather-conditions
    # 01: Clear
    # 02, 03, 04: Clouds
    # 09, 10: Rain
    # 11: Thunderstorm
    # 13: Snow
    # 50: Mist
    
    code_num = icon_code[:2]
    
    if code_num == '01':
        return 'bg-sunny' if is_day else 'bg-night'
    elif code_num in ['02', '03', '04', '50']:
        return 'bg-cloudy'
    elif code_num in ['09', '10']:
        return 'bg-rainy'
    elif code_num == '11':
        return 'bg-stormy'
    elif code_num == '13':
        return 'bg-snowy'
    else:
        return 'bg-default'

def _process_hourly_data(data):
    # Extract next 24 hours (approx 8 items * 3h) from 5-day forecast
    hourly = []
    for item in data['list'][:8]:
        dt = datetime.fromtimestamp(item['dt'])
        hourly.append({
            'time': dt.strftime('%H:%M'),
            'temp': round(item['main']['temp']),
            'icon': item['weather'][0]['icon'],
            'description': item['weather'][0]['description'].capitalize(),
            'rain_prob': int(item.get('pop', 0) * 100)
        })
    return hourly

def _process_onecall_daily(daily_data, lang='en'):
    processed = []
    for item in daily_data[:7]: 
        dt = datetime.fromtimestamp(item['dt'])
        processed.append({
            'date': dt.strftime('%d/%m'),
            'full_date': dt.strftime('%A, %d %B %Y') if lang == 'en' else dt.strftime('%d/%m/%Y'), # Simplification for now, or improve locale handling
            'day_name': dt.strftime('%A'),
            'temp': round(item['temp']['day']),
            'feels_like': round(item['feels_like']['day']),
            'humidity': item['humidity'],
            'wind_speed': item['wind_speed'],
            'description': item['weather'][0]['description'].capitalize(),
            'icon': item['weather'][0]['icon'],
            'rain_prob': int(item.get('pop', 0) * 100)
        })
    return processed

# Take 24h data from OneCall API
def _process_onecall_hourly(hourly_data):
    processed = []
    for item in hourly_data[:24]:
        dt = datetime.fromtimestamp(item['dt'])
        processed.append({
            'time': dt.strftime('%H:%M'),
            'temp': round(item['temp']),
            'icon': item['weather'][0]['icon'],
            'description': item['weather'][0]['description'].capitalize(),
            'rain_prob': int(item.get('pop', 0) * 100)
        })
    return processed

def _process_forecast_data(data):
    daily_map = {}
    
    # Iterate through all 3-hour forecast items
    for item in data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        date_str = dt.strftime('%Y-%m-%d')
        
        # Initialize day entry if not exists
        if date_str not in daily_map:
            daily_map[date_str] = {
                'dt_obj': dt,
                'temps': [],
                'rain_probs': [],
                'weather_conditions': [],
                'humidities': [],
                'wind_speeds': [],
                'pressures': [],
                'visibilities': [],
                'hourly_segments': []
            }
        
        # Collect data for aggregation
        daily_map[date_str]['temps'].append(item['main']['temp'])
        daily_map[date_str]['rain_probs'].append(int(item.get('pop', 0) * 100))
        daily_map[date_str]['weather_conditions'].append((item['weather'][0]['icon'], item['weather'][0]['description']))
        daily_map[date_str]['humidities'].append(item['main']['humidity'])
        daily_map[date_str]['wind_speeds'].append(item['wind']['speed'])
        daily_map[date_str]['pressures'].append(item['main']['pressure'])
        daily_map[date_str]['visibilities'].append(item.get('visibility', 0) / 1000)
        
        # Collect Hourly Segment
        dt = datetime.fromtimestamp(item['dt'])
        daily_map[date_str]['hourly_segments'].append({
            'time': dt.strftime('%H:%M'),
            'temp': round(item['main']['temp']),
            'icon': item['weather'][0]['icon'],
            'description': item['weather'][0]['description'].capitalize(),
            'rain_prob': int(item.get('pop', 0) * 100)
        })

    daily_forecasts = []

    def get_weather_severity(icon_code):
        code_num = icon_code[:2]
        if code_num == '13': return 5 # Snow
        if code_num == '11': return 4 # Thunderstorm
        if code_num in ['09', '10']: return 3 # Rain
        if code_num == '50': return 2 # Mist
        if code_num in ['02', '03', '04']: return 1 # Clouds
        return 0 # Clear (01)

    sorted_dates = sorted(daily_map.keys())
    
    # Create final list (limit to 5 days)
    for date_str in sorted_dates:
        day_data = daily_map[date_str]
        
        # Aggregate Max Temp
        max_temp = round(max(day_data['temps']))
        
        # Aggregate Max Rain Prob
        max_rain_prob = max(day_data['rain_probs'])
        
        # Aggregate Averages/Max for other metrics
        avg_humidity = round(sum(day_data['humidities']) / len(day_data['humidities']))
        max_wind = round(max(day_data['wind_speeds']), 2)
        avg_pressure = round(sum(day_data['pressures']) / len(day_data['pressures']))
        avg_visibility = round(sum(day_data['visibilities']) / len(day_data['visibilities']), 1)

        best_condition = max(day_data['weather_conditions'], key=lambda x: get_weather_severity(x[0]))
        icon, description = best_condition
        
        # Use the stored datetime object for date formatting
        dt = day_data['dt_obj']
        
        daily_forecasts.append({
            'date': dt.strftime('%d/%m'),
            'full_date': dt.strftime('%A, %d %B %Y'),
            'day_name': dt.strftime('%A'),
            'temp': max_temp,
            'feels_like': 0,
            'humidity': avg_humidity,
            'wind_speed': max_wind, 
            'pressure': avg_pressure,
            'visibility': avg_visibility,
            'description': description.capitalize(),
            'icon': icon,
            'rain_prob': max_rain_prob,
            'hourly_segments': day_data['hourly_segments']
        })
        
        if len(daily_forecasts) >= 5:
            break
            
    return daily_forecasts
