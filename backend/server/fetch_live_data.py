import requests
from geopy.distance import geodesic

urls = {
    "air_temperature": "https://api-open.data.gov.sg/v2/real-time/api/air-temperature",
    "rainfall": "https://api-open.data.gov.sg/v2/real-time/api/rainfall",
    "humidity": "https://api-open.data.gov.sg/v2/real-time/api/relative-humidity",
    "wind_speed": "https://api-open.data.gov.sg/v2/real-time/api/wind-speed",
    "wind_direction": "https://api-open.data.gov.sg/v2/real-time/api/wind-direction",
    "two_hr_forecast": "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast",
    "twenty_four_hr_forecast": "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast",
}

def fetch_data(url):
    try:
        response = requests.get(url, timeout=5)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"API fetch failed for {url}: {str(e)}")
        return {}

def find_nearest_station(stations, point):
    min_dist = float('inf')
    nearest_station = None
    for station in stations:
        try:
            # Handle cases where labelLocation might be missing or malformed
            if not station.get('labelLocation'):
                continue
                
            station_lat = station['labelLocation'].get('latitude')
            station_lon = station['labelLocation'].get('longitude')
            
            if station_lat is None or station_lon is None:
                continue
                
            station_loc = (station_lat, station_lon)
            dist = geodesic(point, station_loc).meters
            
            if dist < min_dist:
                min_dist = dist
                nearest_station = station
                
        except (KeyError, TypeError) as e:
            print(f"Skipping station due to error: {e}")
            continue
            
    return nearest_station

def get_weather_features(point):
    print(f"Fetching weather for: {point}")
    lat, lon = point
    features = {
        'air_temperature_c': None,
        'rainfall_mm': None,
        'relative_humidity_percent': None,
        'wind_speed_mps': None,
        'wind_direction_deg': None,
        'forecast_text': None
    }

    try:
        # Fetch live data with error handling
        air_temp_data = fetch_data(urls['air_temperature']).get('data', {})
        print(f"Air temp API response: {air_temp_data}")  # Debug raw response
        rainfall_data = fetch_data(urls['rainfall']).get('data', {})
        humidity_data = fetch_data(urls['humidity']).get('data', {})
        wind_speed_data = fetch_data(urls['wind_speed']).get('data', {})
        wind_dir_data = fetch_data(urls['wind_direction']).get('data', {})
        two_hr_forecast = fetch_data(urls['two_hr_forecast']).get('data', {})

        # Get nearest stations with fallbacks
        temp_station = find_nearest_station(air_temp_data.get('stations', []), (lat, lon)) or {}
        rain_station = find_nearest_station(rainfall_data.get('stations', []), (lat, lon)) or {}
        humid_station = find_nearest_station(humidity_data.get('stations', []), (lat, lon)) or {}
        wind_speed_station = find_nearest_station(wind_speed_data.get('stations', []), (lat, lon)) or {}
        wind_dir_station = find_nearest_station(wind_dir_data.get('stations', []), (lat, lon)) or {}

        # Get readings with defaults
        readings = air_temp_data.get('readings', [{}])[0].get('data', [])
        features['air_temperature_c'] = next(
            (item['value'] for item in readings if item.get('stationId') == temp_station.get('id')),
            None
        )

        readings = rainfall_data.get('readings', [{}])[0].get('data', [])
        features['rainfall_mm'] = next(
            (item['value'] for item in readings if item.get('stationId') == rain_station.get('id')),
            None
        )

        readings = humidity_data.get('readings', [{}])[0].get('data', [])
        features['relative_humidity_percent'] = next(
            (item['value'] for item in readings if item.get('stationId') == humid_station.get('id')),
            None
        )

        readings = wind_speed_data.get('readings', [{}])[0].get('data', [])
        features['wind_speed_mps'] = next(
            (item['value'] for item in readings if item.get('stationId') == wind_speed_station.get('id')),
            None
        )

        readings = wind_dir_data.get('readings', [{}])[0].get('data', [])
        features['wind_direction_deg'] = next(
            (item['value'] for item in readings if item.get('stationId') == wind_dir_station.get('id')),
            None
        )

        # Handle forecast
        area_meta = two_hr_forecast.get('area_metadata', [])
        if area_meta:
            nearest_area = find_nearest_station(area_meta, (lat, lon)) or {}
            area_name = nearest_area.get('name')
            if area_name:
                forecast_item = two_hr_forecast.get('items', [{}])[0].get('forecasts', [])
                features['forecast_text'] = next(
                    (item['forecast'] for item in forecast_item if item.get('area') == area_name),
                    None
                )

    except Exception as e:
        print(f"Error getting weather features: {str(e)}")
    
    return features