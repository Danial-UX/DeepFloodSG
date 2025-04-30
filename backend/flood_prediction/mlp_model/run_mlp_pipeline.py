from .train_mlp import predict_flood
from topography.topo_features import get_topo_features
from server.fetch_live_data import get_weather_features

def run_flood_risk_pipeline(route):
    print(f"First point sample: {route[0]}") 
    print(f"Weather features for first point: {get_weather_features((route[0]['lat'], route[0]['lon']))}")
    print(f"Topo features for first point: {get_topo_features(route[0]['lat'], route[0]['lon'])}")
    
    results = []
    for point in route:
        try:
            lat, lon = point['lat'], point['lon']
            weather = get_weather_features((lat, lon))
            elevation, slope, aspect, drainage_density = get_topo_features(lat, lon)

            # Set safe defaults for missing values
            input_dict = {
                "latitude": lat,
                "longitude": lon,
                "slope_percent": slope if slope is not None else 5.0,
                "aspect_degrees": aspect if aspect is not None else 180.0,
                "drainage_density": drainage_density if drainage_density is not None else 0.2,
                "daily_rainfall_mm": weather["rainfall_mm"] if weather["rainfall_mm"] is not None else 0.0,
                "mean_temp_C": weather["air_temperature_c"] if weather["air_temperature_c"] is not None else 30.0,
                "max_wind_kmh": (weather["wind_speed_mps"] if weather["wind_speed_mps"] is not None else 2.0) * 3.6,
                "elevation_m": elevation if elevation is not None else 15.0
            }

            print(f"Model input: {input_dict}")

            flood_prob = predict_flood(model, dataset, device, input_dict)

            results.append({
                "lat": lat,
                "lon": lon,
                "risk": round(float(flood_prob), 4)  # Ensure numeric value
            })

        except Exception as e:
            print(f"Error processing point {lat},{lon}: {str(e)}")
            results.append({
                "lat": lat,
                "lon": lon,
                "risk": None,
                "error": str(e)
            })

    return results