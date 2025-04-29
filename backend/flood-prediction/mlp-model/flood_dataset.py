import pandas as pd
import torch
from torch.utils.data import Dataset

class FloodTabularDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv("flood_prediction_training_data.csv")
        
        self.features = self.data[[
            "latitude",
            "longitude",
            "slope_percent",
            "aspect_degrees",
            "drainage_density",
            "daily_rainfall_mm",
            "mean_temp_C",
            "max_wind_kmh",
            "elevation_m",
        ]].values
        
        self.labels = self.data["flood_occurred"].values  # 0 (no flood) or 1 (flood)
        
        # Normalize features
        self.features = (self.features - self.features.mean(axis=0)) / (self.features.std(axis=0) + 1e-8)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)