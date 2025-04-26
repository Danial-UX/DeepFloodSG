import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import lightgbm as lgb
import pickle

df = pd.read_csv("flood_data.csv")

# Split Features (X) and Target (y)
# X contains all features (predictor variables)
# y contains the target we want to predict (flood occurrence)
location_names = df["area_name"]

X = df.drop(columns=["flood_occurred", "area_name"])
y = df["flood_occurred"]

# Split data into training and testing sets
# 20% of data is used for testing, 80% for training
# random_state=42 ensures reproducible splits
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Train LightGBM Classifier
lgbm_model = lgb.LGBMClassifier(random_state=42)
lgbm_model.fit(X_train, y_train)

# Evaluate Models
print("Random Forest Results:")
y_pred_rf = rf_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Classification Report:\n", classification_report(y_test, y_pred_rf))

print("\nLightGBM Results:")
y_pred_lgbm = lgbm_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred_lgbm))
print("Classification Report:\n", classification_report(y_test, y_pred_lgbm))

# Map to location names
# predictions = model.predict(X_test)
# results = pd.DataFrame({
#     "area_name": location_names[y_test.index],
#     "actual_flood": y_test,
#     "predicted_flood": predictions
# })

# Save Models
with open('rf_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)

with open('lgbm_model.pkl', 'wb') as f:
    pickle.dump(lgbm_model, f)

print("\nModels trained and saved successfully")