import requests
from geopy.distance import geodesic
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urls = {
    "air_temperature": "https://api-open.data.gov.sg/v2/real-time/api/air-temperature",
    "rainfall": "https://api-open.data.gov.sg/v2/real-time/api/rainfall",
    "humidity": "https://api-open.data.gov.sg/v2/real-time/api/relative-humidity",
    "wind_speed": "https://api-open.data.gov.sg/v2/real-time/api/wind-speed",
    "wind_direction": "https://api-open.data.gov.sg/v2/real-time/api/wind-direction",
    "two_hr_forecast": "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast",
}

# Default values when data is unavailable
DEFAULT_VALUES = {
    'air_temperature_c': 28.0,
    'rainfall_mm': 0.0,
    'relative_humidity_percent': 75.0,
    'wind_speed_mps': 2.0,
    'wind_direction_deg': 180.0,
    'forecast_text': "Fair"
}

def fetch_data(url, max_retries=3):
    """Fetch data from API with retry logic and timeout handling."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"API Response from {url}: {data}")
                return data
            else:
                logger.warning(f"API Error {response.status_code} from {url}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"API fetch failed after {max_retries} attempts for {url}")
    return {}

def find_nearest_station(stations, point, max_distance_km=10):
    """Find nearest station within reasonable distance."""
    if not stations or not point:
        return None
        
    min_dist = float('inf')
    nearest_station = None
    
    for station in stations:
        try:
            location = station.get('location') or station.get('labelLocation') or {}
            station_lat = location.get('latitude')
            station_lon = location.get('longitude')
            
            if None in (station_lat, station_lon):
                continue
                
            station_loc = (float(station_lat), float(station_lon))
            dist = geodesic(point, station_loc).kilometers
            
            if dist < min_dist and dist <= max_distance_km:
                min_dist = dist
                nearest_station = station
                
        except Exception as e:
            logger.warning(f"Skipping station {station.get('id')} due to error: {e}")
            
    return nearest_station if min_dist != float('inf') else None

def get_latest_readings(data):
    """Get the most recent readings from API response."""
    if not data or not data.get('items'):
        return None
        
    try:
        # Sort items by timestamp (newest first)
        sorted_items = sorted(data['items'], 
                           key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%dT%H:%M:%S%z'), 
                           reverse=True)
        
        # Get readings from the most recent item
        return sorted_items[0].get('readings', []) if sorted_items else None
    except Exception as e:
        logger.error(f"Error processing readings: {e}")
        return None

def get_weather_features(point, use_defaults=True):
    """Get comprehensive weather features for a given point."""
    logger.info(f"Fetching weather for: {point}")
    lat, lon = point
    
    # Initialize with defaults if enabled
    features = DEFAULT_VALUES.copy() if use_defaults else {
        'air_temperature_c': None,
        'rainfall_mm': None,
        'relative_humidity_percent': None,
        'wind_speed_mps': None,
        'wind_direction_deg': None,
        'forecast_text': None
    }

    try:
        # Fetch all data in parallel (consider using threading for better performance)
        air_temp_data = fetch_data(urls['air_temperature']).get('data', {})
        rainfall_data = fetch_data(urls['rainfall']).get('data', {})
        humidity_data = fetch_data(urls['humidity']).get('data', {})
        wind_speed_data = fetch_data(urls['wind_speed']).get('data', {})
        wind_dir_data = fetch_data(urls['wind_direction']).get('data', {})
        two_hr_forecast = fetch_data(urls['two_hr_forecast']).get('data', {})

        # Process each weather parameter
        def get_parameter_value(data, param_name, point):
            station = find_nearest_station(data.get('stations', []), point)
            if not station:
                return None
                
            readings = get_latest_readings(data)
            if not readings:
                return None
                
            return next(
                (float(r['value']) for r in readings if r.get('stationId') == station.get('id')),
                None
            )

        # Temperature
        features['air_temperature_c'] = get_parameter_value(air_temp_data, 'temperature', point) or features.get('air_temperature_c')

        # Rainfall
        features['rainfall_mm'] = get_parameter_value(rainfall_data, 'rainfall', point) or features.get('rainfall_mm')

        # Humidity
        features['relative_humidity_percent'] = get_parameter_value(humidity_data, 'humidity', point) or features.get('relative_humidity_percent')

        # Wind speed
        features['wind_speed_mps'] = get_parameter_value(wind_speed_data, 'wind_speed', point) or features.get('wind_speed_mps')

        # Wind direction
        features['wind_direction_deg'] = get_parameter_value(wind_dir_data, 'wind_direction', point) or features.get('wind_direction_deg')

        # Forecast
        area_meta = two_hr_forecast.get('area_metadata', [])
        forecast_items = two_hr_forecast.get('items', [{}])
        
        if area_meta and forecast_items:
            nearest_area = find_nearest_station(area_meta, point)
            if nearest_area:
                area_name = nearest_area.get('name')
                latest_forecast = forecast_items[0].get('forecasts', [])
                features['forecast_text'] = next(
                    (item['forecast'] for item in latest_forecast if item.get('area') == area_name),
                    features.get('forecast_text')
                )

    except Exception as e:
        logger.error(f"Error getting weather features: {str(e)}")
        if not use_defaults:
            return None

    logger.info(f"Weather features: {features}")
    return features