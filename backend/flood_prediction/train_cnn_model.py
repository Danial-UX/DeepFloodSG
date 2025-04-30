import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import rasterio
import numpy as np
import torch.nn.functional as F

# 1. Dataset class
class FloodDataset(Dataset):
    def __init__(self, image_path, label_path, patch_size=5):
        self.image = rasterio.open(image_path).read().astype(np.float32)  # Shape: (C, H, W)
        self.label = rasterio.open(label_path).read(1)  # Shape: (H, W)
        self.patch_size = patch_size
        self.image = (self.image - self.image.mean()) / self.image.std()  # Normalize
        self.valid_indices = []
        for idx in range((self.image.shape[1] - patch_size + 1) * (self.image.shape[2] - patch_size + 1)):
            h = idx // (self.image.shape[2] - patch_size + 1)
            w = idx % (self.image.shape[2] - patch_size + 1)
            lbl = self.label[h + patch_size//2, w + patch_size//2]
            if lbl != 255:  # Only include valid pixels
                self.valid_indices.append(idx)

    def __len__(self):
        return len(self.valid_indices)

    def __getitem__(self, idx):
        # Convert idx to (h, w) coordinates
        real_idx = self.valid_indices[idx]
        h = real_idx // (self.image.shape[2] - self.patch_size + 1)
        w = real_idx % (self.image.shape[2] - self.patch_size + 1)

        # Extract patch (C, patch_size, patch_size)
        img_patch = self.image[:, h:h+self.patch_size, w:w+self.patch_size]
        lbl = self.label[h + self.patch_size//2, w + self.patch_size//2]
        
        if lbl == 255:
            lbl = -1
        return torch.from_numpy(img_patch), torch.tensor(lbl, dtype=torch.long)

# 2. CNN Model
class FloodCNN(nn.Module):
    def __init__(self, patch_size=5):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),  # (16, patch_size, patch_size)
            nn.ReLU(),
            nn.MaxPool2d(2),  # (16, patch_size//2, patch_size//2)
            nn.Conv2d(16, 32, kernel_size=3, padding=1),  # (32, patch_size//2, patch_size//2)
            nn.ReLU(),
            nn.MaxPool2d(2)  # (32, patch_size//4, patch_size//4)
        )
        self.fc = nn.Sequential(
            nn.Linear(32 * (patch_size//4)**2, 64),  # Adjust for your patch_size
            nn.ReLU(),
            nn.Dropout(0.5),  # Regularization
            nn.Linear(64, 2)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)  # Flatten
        return self.fc(x)

# 3. Load data
dataset = FloodDataset(
    image_path='../rastors/stacked_features.tif',
    label_path='flood_label.tif'
)

# Filter out invalid labels (255)
valid_data = [(x, y) for x, y in dataset if y != -1]
inputs, targets = zip(*valid_data)

inputs = torch.stack(inputs)
targets = torch.stack(targets)

# Split into train/test
split = int(0.8 * len(inputs))
train_inputs, test_inputs = inputs[:split], inputs[split:]
train_targets, test_targets = targets[:split], targets[split:]

train_dataset = torch.utils.data.TensorDataset(train_inputs, train_targets)
test_dataset = torch.utils.data.TensorDataset(test_inputs, test_targets)

train_loader = DataLoader(dataset, batch_size=512, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)

# 4. Train model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = FloodCNN(patch_size=5).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 5. Training loop
epochs = 10

for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch_inputs, batch_targets in train_loader:
        batch_inputs = batch_inputs.to(device)
        batch_targets = batch_targets.to(device)

        optimizer.zero_grad()
        outputs = model(batch_inputs)
        loss = criterion(outputs, batch_targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

# 6. Test
model.eval()
flood_probs_list = []
true_labels_list = []

with torch.no_grad():
    for batch_inputs, batch_targets in test_loader:
        batch_inputs = batch_inputs.to(device)
        batch_targets = batch_targets.to(device)

        outputs = model(batch_inputs) # outputs: (batch_size, 2)
        probs = F.softmax(outputs, dim=1)

        flood_probs = probs[:, 1]  # probability of flood
        flood_probs_list.extend(flood_probs.cpu().numpy())
        true_labels_list.extend(batch_targets.cpu().numpy())

# flood_probs_list contains probability for each test pixel

# Thresholding if hard classification
preds = (np.array(flood_probs_list) > 0.5).astype(int)
correct = (preds == np.array(true_labels_list)).sum()
accuracy = correct / len(true_labels_list)

print(f"Test Accuracy: {accuracy:.2f}")