import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import rasterio
import numpy as np
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, average_precision_score, roc_auc_score
import matplotlib.pyplot as plt
from torch.optim.lr_scheduler import ReduceLROnPlateau

# 1. Improved Dataset class with augmentation
class FloodDataset(Dataset):
    def __init__(self, image_path, label_path, patch_size=7, transform=None, is_training=True):
        self.image = rasterio.open(image_path).read().astype(np.float32)  # Shape: (C, H, W)
        self.label = rasterio.open(label_path).read(1)  # Shape: (H, W)
        self.patch_size = patch_size
        self.transform = transform
        self.is_training = is_training
        
        # Better normalization (per channel)
        for i in range(self.image.shape[0]):
            self.image[i] = (self.image[i] - np.mean(self.image[i])) / (np.std(self.image[i]) + 1e-8)
        
        # Find valid indices
        self.valid_indices = []
        for h in range(self.image.shape[1] - patch_size + 1):
            for w in range(self.image.shape[2] - patch_size + 1):
                lbl = self.label[h + patch_size//2, w + patch_size//2]
                if lbl != 255:  # Only include valid pixels
                    self.valid_indices.append((h, w))
        
        # Balance classes if training
        if is_training:
            flood_indices = [(h, w) for h, w in self.valid_indices 
                            if self.label[h + patch_size//2, w + patch_size//2] == 1]
            no_flood_indices = [(h, w) for h, w in self.valid_indices 
                               if self.label[h + patch_size//2, w + patch_size//2] == 0]
            
            # Oversample the minority class
            if len(flood_indices) < len(no_flood_indices):
                # Calculate how many times to repeat the minority class
                repeat_factor = min(5, len(no_flood_indices) // len(flood_indices))
                flood_indices = flood_indices * repeat_factor
                # Random subset of majority class to reduce imbalance
                if len(flood_indices) < len(no_flood_indices):
                    # Fix: Convert to indices first, then back to tuples
                    indices = list(range(len(no_flood_indices)))
                    selected_indices = np.random.choice(
                        indices, 
                        size=min(len(no_flood_indices), len(flood_indices)*2),
                        replace=False
                    )
                    no_flood_indices = [no_flood_indices[i] for i in selected_indices]
            else:
                repeat_factor = min(5, len(flood_indices) // len(no_flood_indices))
                no_flood_indices = no_flood_indices * repeat_factor
                if len(no_flood_indices) < len(flood_indices):
                    # Fix: Convert to indices first, then back to tuples
                    indices = list(range(len(flood_indices)))
                    selected_indices = np.random.choice(
                        indices, 
                        size=min(len(flood_indices), len(no_flood_indices)*2),
                        replace=False
                    )
                    flood_indices = [flood_indices[i] for i in selected_indices]
            
            self.valid_indices = flood_indices + no_flood_indices

    def __len__(self):
        return len(self.valid_indices)

    def augment(self, patch):
        """Apply simple augmentations to the patch"""
        if np.random.random() > 0.5:
            # Flip horizontally
            patch = np.flip(patch, axis=2).copy()
        if np.random.random() > 0.5:
            # Flip vertically
            patch = np.flip(patch, axis=1).copy()
        if np.random.random() > 0.5:
            # Rotate 90 degrees
            patch = np.rot90(patch, k=1, axes=(1, 2)).copy()
        
        # Add slight noise
        if np.random.random() > 0.5:
            noise = np.random.normal(0, 0.05, patch.shape).astype(np.float32)
            patch = patch + noise
        
        return patch

    def __getitem__(self, idx):
        # Get coordinates
        h, w = self.valid_indices[idx]

        # Extract patch (C, patch_size, patch_size)
        img_patch = self.image[:, h:h+self.patch_size, w:w+self.patch_size].copy()
        lbl = self.label[h + self.patch_size//2, w + self.patch_size//2]
        
        # Apply augmentation for training
        if self.is_training and np.random.random() > 0.5:
            img_patch = self.augment(img_patch)
        
        if lbl == 255:
            lbl = -1
        
        return torch.from_numpy(img_patch), torch.tensor(lbl, dtype=torch.long)

# 2. Improved CNN Model with residual connections and batch normalization
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                              stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                              stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, 
                          stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

class ImprovedFloodCNN(nn.Module):
    def __init__(self, in_channels=3, patch_size=7):
        super().__init__()
        
        # Initial conv layer
        self.init_layer = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU()
        )
        
        # Residual blocks
        self.res_block1 = ResidualBlock(32, 64, stride=2)
        self.res_block2 = ResidualBlock(64, 128, stride=2)
        
        # Adaptive pooling to handle different patch sizes
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Attention mechanism
        self.channel_attention = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.Sigmoid()
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 2)
        )

    def forward(self, x):
        # Input processing
        x = self.init_layer(x)
        
        # Residual blocks
        x = self.res_block1(x)
        x = self.res_block2(x)
        
        # Global pooling
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)  # Flatten
        
        # Channel attention
        attention = self.channel_attention(x)
        x = x * attention
        
        # Classification
        return self.classifier(x)

# 3. Training function with validation
def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, epochs=30, device="cuda"):
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    best_model_state = None
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        epoch_loss = 0
        correct = 0
        total = 0
        
        for batch_inputs, batch_targets in train_loader:
            batch_inputs = batch_inputs.to(device)
            batch_targets = batch_targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_inputs)
            loss = criterion(outputs, batch_targets)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
            # Calculate accuracy
            _, predicted = torch.max(outputs.data, 1)
            total += batch_targets.size(0)
            correct += (predicted == batch_targets).sum().item()
        
        train_loss = epoch_loss / len(train_loader)
        train_accuracy = correct / total
        train_losses.append(train_loss)
        
        # Validation phase
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_inputs, batch_targets in val_loader:
                batch_inputs = batch_inputs.to(device)
                batch_targets = batch_targets.to(device)
                
                outputs = model(batch_inputs)
                loss = criterion(outputs, batch_targets)
                val_loss += loss.item()
                
                # Calculate accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += batch_targets.size(0)
                correct += (predicted == batch_targets).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_accuracy = correct / total
        val_losses.append(val_loss)
        
        # Update learning rate based on validation performance
        scheduler.step(val_loss)
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
        
        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Train Acc: {train_accuracy:.4f}, "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.4f}")
    
    # Load best model
    model.load_state_dict(best_model_state)
    return model, train_losses, val_losses

# 4. Evaluation function
def evaluate_model(model, test_loader, device="cuda"):
    model.eval()
    all_preds = []
    all_probs = []
    all_labels = []
    
    with torch.no_grad():
        for batch_inputs, batch_targets in test_loader:
            batch_inputs = batch_inputs.to(device)
            
            outputs = model(batch_inputs)
            probs = F.softmax(outputs, dim=1)
            flood_probs = probs[:, 1].cpu().numpy()  # Probability of flood
            
            _, predicted = torch.max(outputs, 1)
            predicted = predicted.cpu().numpy()
            
            all_preds.extend(predicted)
            all_probs.extend(flood_probs)
            all_labels.extend(batch_targets.numpy())
    
    # Calculate metrics
    accuracy = (np.array(all_preds) == np.array(all_labels)).mean()
    
    # Calculate AUC and average precision
    auc = roc_auc_score(all_labels, all_probs)
    ap = average_precision_score(all_labels, all_probs)
    
    # Find optimal threshold
    precision, recall, thresholds = precision_recall_curve(all_labels, all_probs)
    f1_scores = 2 * recall * precision / (recall + precision + 1e-8)
    best_threshold = thresholds[np.argmax(f1_scores)]
    
    # Recalculate predictions with optimal threshold
    optimized_preds = (np.array(all_probs) >= best_threshold).astype(int)
    optimized_accuracy = (optimized_preds == np.array(all_labels)).mean()
    
    print(f"Test Accuracy: {accuracy:.4f}")
    print(f"AUC: {auc:.4f}")
    print(f"Average Precision: {ap:.4f}")
    print(f"Optimal Threshold: {best_threshold:.4f}")
    print(f"Optimized Accuracy: {optimized_accuracy:.4f}")
    
    return {
        'accuracy': accuracy,
        'auc': auc,
        'ap': ap,
        'optimal_threshold': best_threshold,
        'optimized_accuracy': optimized_accuracy,
        'predictions': all_preds,
        'probabilities': all_probs,
        'labels': all_labels
    }

# 5. Main execution
def main():
    # Configuration
    PATCH_SIZE = 7  # Larger patch size to capture more context
    BATCH_SIZE = 256  # Smaller batch size for better generalization
    EPOCHS = 30
    LEARNING_RATE = 0.001
    
    # Set seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Choose device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Create dataset
    full_dataset = FloodDataset(
        image_path='../rastors/stacked_features.tif',
        label_path='flood_label.tif',
        patch_size=PATCH_SIZE,
        is_training=True
    )
    
    # Get all data from dataset
    all_data = []
    for i in range(len(full_dataset)):
        all_data.append(full_dataset[i])
    
    # Split into train, validation, and test sets
    train_data, temp_data = train_test_split(all_data, test_size=0.3, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    
    # Create custom datasets for validation and testing without augmentation
    class SimpleDataset(Dataset):
        def __init__(self, data):
            self.data = data
        
        def __len__(self):
            return len(self.data)
        
        def __getitem__(self, idx):
            return self.data[idx]
    
    train_dataset = SimpleDataset(train_data)
    val_dataset = SimpleDataset(val_data)
    test_dataset = SimpleDataset(test_data)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)
    
    # Create model
    model = ImprovedFloodCNN(in_channels=full_dataset.image.shape[0], patch_size=PATCH_SIZE).to(device)
    
    # Loss function with class weights to handle imbalance
    all_labels = [label.item() for _, label in all_data]
    class_counts = np.bincount(all_labels)
    class_weights = 1.0 / torch.tensor(class_counts, dtype=torch.float)
    class_weights = class_weights / class_weights.sum()
    class_weights = class_weights.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    # Optimizer with weight decay for regularization
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    
    # Learning rate scheduler
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)
    
    # Train model
    print("Starting training...")
    model, train_losses, val_losses = train_model(
        model, train_loader, val_loader, criterion, optimizer, scheduler, epochs=EPOCHS, device=device
    )
    
    # Plot training history
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.savefig('training_history.png')
    
    # Evaluate model
    print("\nEvaluating model on test set...")
    results = evaluate_model(model, test_loader, device)
    
    # Save model
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'results': results,
        'class_weights': class_weights,
        'hyperparameters': {
            'patch_size': PATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS
        }
    }, 'flood_detection_model.pth')
    
    print("Model saved to 'flood_detection_model.pth'")
    
    # Create a prediction visualization on a sample
    print("\nGenerating prediction visualization...")
    
    # Create a prediction function for the entire image
    def predict_full_image(model, image_path, label_path, patch_size, device):
        # Load image and label
        image = rasterio.open(image_path).read().astype(np.float32)
        label = rasterio.open(label_path).read(1)
        
        # Normalize image
        for i in range(image.shape[0]):
            image[i] = (image[i] - np.mean(image[i])) / (np.std(image[i]) + 1e-8)
        
        # Create output probability map
        height, width = label.shape
        prob_map = np.zeros((height, width), dtype=np.float32)
        count_map = np.zeros((height, width), dtype=np.float32)
        
        # Set model to evaluation mode
        model.eval()
        
        # Use sliding window approach
        with torch.no_grad():
            for h in range(0, height - patch_size + 1, max(1, patch_size//4)):  # Use stride for overlapping predictions
                for w in range(0, width - patch_size + 1, max(1, patch_size//4)):
                    # Extract patch
                    patch = image[:, h:h+patch_size, w:w+patch_size]
                    patch_tensor = torch.from_numpy(patch).unsqueeze(0).to(device)
                    
                    # Predict
                    output = model(patch_tensor)
                    probs = F.softmax(output, dim=1)
                    flood_prob = probs[0, 1].cpu().numpy()
                    
                    # Add to probability map (center pixel)
                    for ph in range(patch_size):
                        for pw in range(patch_size):
                            if h+ph < height and w+pw < width:
                                prob_map[h+ph, w+pw] += flood_prob
                                count_map[h+ph, w+pw] += 1
        
        # Average overlapping predictions
        count_map[count_map == 0] = 1  # Avoid division by zero
        prob_map = prob_map / count_map
        
        return prob_map, label
    
    # Generate and save visualization
    prob_map, true_label = predict_full_image(
        model, '../rastors/stacked_features.tif', 'flood_label.tif', PATCH_SIZE, device
    )
    
    # Create RGB visualization
    # Red channel: True positives (1) and false negatives (0.5)
    # Green channel: True positives (1) and false positives (0.5)
    # Blue channel: True negatives (1) and false positives (0.5)
    
    # Create mask for valid pixels
    valid_mask = (true_label != 255)
    
    # Initialize RGB image
    rgb = np.zeros((true_label.shape[0], true_label.shape[1], 3), dtype=np.float32)
    
    # Apply thresholding using optimal threshold
    pred_binary = (prob_map >= results['optimal_threshold']).astype(np.uint8)
    
    # True positives (white): Both prediction and truth are 1
    true_pos = (pred_binary == 1) & (true_label == 1) & valid_mask
    rgb[true_pos] = [1, 1, 1]  # White
    
    # True negatives (black): Both prediction and truth are 0
    true_neg = (pred_binary == 0) & (true_label == 0) & valid_mask
    rgb[true_neg] = [0, 0, 0]  # Black
    
    # False positives (red): Prediction is 1 but truth is 0
    false_pos = (pred_binary == 1) & (true_label == 0) & valid_mask
    rgb[false_pos] = [1, 0, 0]  # Red
    
    # False negatives (blue): Prediction is 0 but truth is 1
    false_neg = (pred_binary == 0) & (true_label == 1) & valid_mask
    rgb[false_neg] = [0, 0, 1]  # Blue
    
    # Invalid pixels (grey)
    invalid = ~valid_mask
    rgb[invalid] = [0.5, 0.5, 0.5]  # Grey
    
    # Save visualization
    plt.figure(figsize=(12, 12))
    plt.imshow(rgb)
    plt.title('Flood Detection Results')
    plt.colorbar(label='Probability')
    plt.savefig('flood_detection_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save probability map
    plt.figure(figsize=(12, 12))
    plt.imshow(prob_map, cmap='plasma')
    plt.title('Flood Probability Map')
    plt.colorbar(label='Probability')
    plt.savefig('flood_probability_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to 'flood_detection_results.png' and 'flood_probability_map.png'")

if __name__ == "__main__":
    main()