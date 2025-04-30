import torch
from .train_mlp import FloodMLP, FloodTabularDataset, predict_flood
import os
from .train_mlp import predict_flood
from topography.topo_features import get_topo_features
from server.fetch_live_data import get_weather_features
from pyproj import Transformer

# Initialize model components (singleton pattern)
_MODEL = None
_DATASET = None
_DEVICE = None

def initialize_ml_resources():
    global _MODEL, _DATASET, _DEVICE
    if _MODEL is None:
        csv_file = 'flood_prediction_training_data.csv'
        _DATASET = FloodTabularDataset(csv_file)
        _MODEL = FloodMLP(input_dim=_DATASET.features.shape[1])
        
        model_path = os.path.join(os.path.dirname(__file__), 'flood_model.pth')
        _MODEL.load_state_dict(torch.load(model_path, map_location='cpu'))
        _MODEL.eval()
        
        _DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        _MODEL.to(_DEVICE)
    
    return _MODEL, _DATASET, _DEVICE

def run_flood_risk_pipeline(route):
    # Initialize ML resources
    model, dataset, device = initialize_ml_resources()
    
    # Initialize coordinate transformer (singleton pattern)
    transformer = None
    dem_crs = None
    
    # Get DEM CRS if exists
    dem_path = os.path.join(os.path.dirname(__file__), 'dem_AW3D30_UTM.tif')
    if os.path.exists(dem_path):
        with rasterio.open(dem_path) as dem_src:
            dem_crs = dem_src.crs
            transformer = Transformer.from_crs("EPSG:4326", dem_crs, always_xy=True)
    
    results = []
    for point in route:
        try:
            lat, lon = point['lat'], point['lon']
            
            # Transform coordinates if DEM exists
            utm_x, utm_y = None, None
            if transformer:
                try:
                    utm_x, utm_y = transformer.transform(lon, lat)
                    logger.info(f"Transformed coordinates: {lon},{lat} -> {utm_x},{utm_y}")
                except Exception as e:
                    logger.error(f"Coordinate transform failed for {lon},{lat}: {e}")
            
            # Get features
            weather = get_weather_features((lat, lon))
            elevation, slope, aspect, drainage = get_topo_features(lat, lon)
            
            # Prepare input with defaults
            input_dict = {
                "latitude": lat,
                "longitude": lon,
                "utm_x": utm_x if utm_x else 0.0,  # Add transformed coordinates
                "utm_y": utm_y if utm_y else 0.0,
                "slope_percent": slope if slope is not None else 5.0,
                "aspect_degrees": aspect if aspect is not None else 180.0,
                "drainage_density": drainage if drainage is not None else 0.2,
                "daily_rainfall_mm": weather.get("rainfall_mm", 0.0),
                "mean_temp_C": weather.get("air_temperature_c", 30.0),
                "max_wind_kmh": weather.get("wind_speed_mps", 2.0) * 3.6,
                "elevation_m": elevation if elevation is not None else 15.0
            }

            # Get prediction
            risk = predict_flood(model, dataset, device, input_dict)
            
            results.append({
                "lat": lat,
                "lon": lon,
                "risk": round(float(risk), 4),
                "utm_x": utm_x,
                "utm_y": utm_y,
                "dem_available": transformer is not None
            })
            
        except Exception as e:
            logger.error(f"Error processing point {point}: {str(e)}")
            results.append({
                "lat": lat,
                "lon": lon,
                "risk": None,
                "error": str(e),
                "dem_available": transformer is not None
            })
    
    return results