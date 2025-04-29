import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import os

# 1. Dataset
class FloodTabularDataset(Dataset):
    def __init__(self, csv_file):
        csv_path = os.path.join(os.path.dirname(__file__), "flood_prediction_training_data.csv")
        self.data = pd.read_csv(csv_path)
        
        # Features
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
        
        # Labels
        self.labels = self.data["flood_occurred"].values  # 0 (no flood) or 1 (flood)

        # Normalize features
        self.mean = self.features.mean(axis=0)
        self.std = self.features.std(axis=0) + 1e-8
        self.features = (self.features - self.mean) / self.std

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

# 2. Model
class FloodMLP(nn.Module):
    def __init__(self, input_dim):
        super(FloodMLP, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 2)  # Output: flood / no flood
        )

    def forward(self, x):
        return self.model(x)

# 3. Train and Test
def train_and_evaluate(csv_file, epochs=20, batch_size=64):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load dataset
    dataset = FloodTabularDataset(csv_file)
    input_dim = dataset.features.shape[1]

    # Train/test split
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Model, optimizer, loss
    model = FloodMLP(input_dim=input_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for features, labels in train_loader:
            features, labels = features.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

    # Evaluation
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for features, labels in test_loader:
            features, labels = features.to(device), labels.to(device)
            outputs = model(features)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    torch.save(model.state_dict(), 'flood_model.pth')

    print(f"Test Accuracy: {correct/total:.4f}")

    return model, dataset, device

# 4. Inference Function
def predict_flood(model, dataset, device, input_dict):
    input_order = [
        "latitude",
        "longitude",
        "slope_percent",
        "aspect_degrees",
        "drainage_density",
        "daily_rainfall_mm",
        "mean_temp_C",
        "max_wind_kmh",
        "elevation_m"
    ]

    input_data = torch.tensor([
        [input_dict[feature] for feature in input_order]
    ], dtype=torch.float32)

    # Normalize with training set stats
    input_data = (input_data - torch.tensor(dataset.mean, dtype=torch.float32)) / torch.tensor(dataset.std, dtype=torch.float32)
    input_data = input_data.to(device)

    model.eval()
    with torch.no_grad():
        output = model(input_data)
        probs = F.softmax(output, dim=1)
        flood_prob = probs[0, 1].item()  # probability of flood

    return flood_prob

# 5. Main Script to Run Everything
if __name__ == "__main__":
    csv_file = 'flood_prediction_training_data.csv'
    model, dataset, device = train_and_evaluate(csv_file, epochs=20, batch_size=64)

    # Example inference
    live_input = {
        "latitude": 1.3,
        "longitude": 103.8,
        "slope_percent": 5,
        "aspect_degrees": 45,
        "drainage_density": 0.2,
        "daily_rainfall_mm": 3,
        "mean_temp_C": 30,
        "max_wind_kmh": 7.2,
        "elevation_m": 15
    }

    flood_risk = predict_flood(model, dataset, device, live_input)
    print(f"Predicted Flood Risk Probability: {flood_risk:.4f}")