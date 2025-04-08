import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import joblib

MODEL_PATH = 'rf_model.pkl'
ENCODER_PATH = 'label_encoder.pkl'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "sg_rainfall_dataset.csv")

# Load or train model and encoder
if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    rf_model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
else:
    # Train if not already saved
    df = pd.read_csv(csv_file)
    le = LabelEncoder()
    df['location_encoded'] = le.fit_transform(df['location'])

    X = df[['rainfall_mm', 'location_encoded']]
    y = df['flood_risk']

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X, y)

    joblib.dump(rf_model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)

# Predict function
def predict_flood_risk(location_name, rainfall_mm):
    loc_code = le.transform([location_name])[0]
    input_df = pd.DataFrame([[rainfall_mm, loc_code]], columns=['rainfall_mm', 'location_encoded'])
    risk = rf_model.predict(input_df)[0]
    return round(risk, 4)

# Example usage
# print(predict_flood_risk("Tampines", 0))
# print(predict_flood_risk("Tampines", 80))
# print(predict_flood_risk("Bukit Timah", 0))
# print(predict_flood_risk("Bukit Timah", 80))