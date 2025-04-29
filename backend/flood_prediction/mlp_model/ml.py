import torch
from .train_mlp import FloodMLP, FloodTabularDataset, predict_flood
import os

csv_file = 'flood_prediction_training_data.csv'

dataset = FloodTabularDataset("csv_file")
input_dim = dataset.features.shape[1]

model = FloodMLP(input_dim=input_dim)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'flood_model.pth')
model.load_state_dict(torch.load(model_path, map_location='cpu'))

model.eval()

device = torch.device('cpu')
model.to(device)

def get_mock_features(lat, lon):
    # Replace with GIS and weather API data in future
    return {
        "latitude": lat,
        "longitude": lon,
        "slope_percent": 3.5,
        "aspect_degrees": 45,
        "drainage_density": 0.12,
        "daily_rainfall_mm": 5,
        "mean_temp_C": 29.5,
        "max_wind_kmh": 7.2,
        "elevation_m": 12,
    }

def predict_route_risks(route_coords):
    results = []

    for lat, lon in route_coords:
        features = get_mock_features(lat, lon)
        risk = predict_flood(model, dataset, device, features)
        results.append({
            "lat": lat,
            "lon": lon,
            "risk": risk
        })

    return results
