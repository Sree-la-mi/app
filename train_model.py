import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestRegressor

DATASET_PATH = "load_scheduling_data.csv"
MODEL_PATH = "load_scheduler_model.pkl"

def save_training_data(power, duration, price, constraint, start_time, has_start_time, optimized_time):
    """Append new training data to the dataset."""
    df = pd.DataFrame([[power, duration, price, constraint, start_time, has_start_time, optimized_time]],
                      columns=["power", "duration", "price", "constraint", "start_time", "has_start_time", "optimized_time"])
    
    if os.path.exists(DATASET_PATH):
        df.to_csv(DATASET_PATH, mode='a', header=False, index=False)
    else:
        df.to_csv(DATASET_PATH, index=False)

def train_regression_model():
    """Train the regression model using available data."""
    if not os.path.exists(DATASET_PATH):
        print("⚠️ No dataset found. Creating a sample dataset...")
        create_initial_dataset()

    df = pd.read_csv(DATASET_PATH)
    X = df[["power", "duration", "price", "constraint", "start_time", "has_start_time"]]
    y = df["optimized_time"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("✅ Model retrained successfully!")

def create_initial_dataset():
    """Generate a sample dataset if it does not exist."""
    if not os.path.exists(DATASET_PATH):
        data = {
            "power": [2.5, 1.8, 3.2],
            "duration": [3, 2, 4],
            "price": [0.12, 0.15, 0.10],
            "constraint": [0, 1, 2],
            "start_time": [8, -1, 23],
            "has_start_time": [1, 0, 1],
            "optimized_time": [8.5, 18.0, 22.5]
        }
        df = pd.DataFrame(data)
        df.to_csv(DATASET_PATH, index=False)
        print(f"✅ Created {DATASET_PATH} successfully!")
