from flood_prediction.mlp_model.ml import predict_flood, model, dataset, device
from server.fetch_live_data import get_weather_features
from topography.topo_features import get_topo_features

def run_flood_risk_pipeline(route):
    results = []
    for lat, lon in route:
        try:
            weather = get_weather_features((lat, lon))
            elevation, slope, aspect, drainage_density = get_topo_features(lat, lon)

            slope = slope if slope is not None else 5.0
            aspect = aspect if aspect is not None else 180.0
            drainage_density = drainage_density if drainage_density is not None else 0.2

            input_dict = {
                "latitude": lat,
                "longitude": lon,
                "slope_percent": slope,
                "aspect_degrees": aspect,
                "drainage_density": drainage_density,
                "daily_rainfall_mm": weather["rainfall_mm"] or 0.0,
                "mean_temp_C": weather["air_temperature_c"] or 30.0,
                "max_wind_kmh": (weather["wind_speed_mps"] or 2.0) * 3.6,
                "elevation_m": elevation if elevation is not None else 15.0
            }

            flood_prob = predict_flood(model, dataset, device, input_dict)

            results.append({
                "lat": lat,
                "lon": lon,
                "risk": round(flood_prob, 4)
            })
        except Exception as e:
            results.append({
                "lat": lat,
                "lon": lon,
                "risk": None,
                "error": str(e)
            })

    return results
