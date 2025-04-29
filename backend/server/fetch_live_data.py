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

# Helper: Fetch API
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Helper: Find nearest station
def find_nearest_station(stations, point):
    min_dist = float('inf')
    nearest_station = None
    for station in stations:
        station_loc = (station['labelLocation']['latitude'], station['labelLocation']['longitude'])
        dist = geodesic(point, station_loc).meters
        if dist < min_dist:
            min_dist = dist
            nearest_station = station
    return nearest_station

# Get weather data for a point
def get_weather_features(point):
    lat, lon = point
    features = {}

    # Fetch live data
    air_temp_data = fetch_data(urls['air_temperature'])['data']
    rainfall_data = fetch_data(urls['rainfall'])['data']
    humidity_data = fetch_data(urls['humidity'])['data']
    wind_speed_data = fetch_data(urls['wind_speed'])['data']
    wind_dir_data = fetch_data(urls['wind_direction'])['data']
    two_hr_forecast = fetch_data(urls['two_hr_forecast'])['data']

    # Nearest stations
    temp_station = find_nearest_station(air_temp_data['stations'], (lat, lon))
    rain_station = find_nearest_station(rainfall_data['stations'], (lat, lon))
    humid_station = find_nearest_station(humidity_data['stations'], (lat, lon))
    wind_speed_station = find_nearest_station(wind_speed_data['stations'], (lat, lon))
    wind_dir_station = find_nearest_station(wind_dir_data['stations'], (lat, lon))

    # Latest readings
    temp_reading = next((item for item in air_temp_data['readings'][0]['data'] if item['stationId'] == temp_station['id']), None)
    rain_reading = next((item for item in rainfall_data['readings'][0]['data'] if item['stationId'] == rain_station['id']), None)
    humid_reading = next((item for item in humidity_data['readings'][0]['data'] if item['stationId'] == humid_station['id']), None)
    wind_speed_reading = next((item for item in wind_speed_data['readings'][0]['data'] if item['stationId'] == wind_speed_station['id']), None)
    wind_dir_reading = next((item for item in wind_dir_data['readings'][0]['data'] if item['stationId'] == wind_dir_station['id']), None)

    features['air_temperature_c'] = temp_reading['value'] if temp_reading else None
    features['rainfall_mm'] = rain_reading['value'] if rain_reading else None
    features['relative_humidity_percent'] = humid_reading['value'] if humid_reading else None
    features['wind_speed_mps'] = wind_speed_reading['value'] if wind_speed_reading else None
    features['wind_direction_deg'] = wind_dir_reading['value'] if wind_dir_reading else None

    # Forecast
    nearest_area = find_nearest_station(two_hr_forecast['area_metadata'], (lat, lon))
    area_name = nearest_area['name']
    forecast = next((item['forecast'] for item in two_hr_forecast['items'][0]['forecasts'] if item['area'] == area_name), None)
    features['forecast_text'] = forecast

    return features