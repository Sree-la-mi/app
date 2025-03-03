import pandas as pd
import os

DATASET_PATH = "load_scheduling_data.csv"

def create_initial_dataset():
    """Generates the CSV file with sample data if it does not exist."""
    if not os.path.exists(DATASET_PATH):
        print("⚡ Generating initial dataset...")

        data = {
            "power": [2.5, 1.8, 3.2],
            "duration": [3, 2, 4],
            "constraint": [0, 1, 2],  # Encoded constraint values (Morning, Evening, Night)
            "start_time": [8, -1, 23],  # -1 means no predefined start time
            "has_start_time": [1, 0, 1],  # 1 = True, 0 = False
            "optimized_time": [8.5, 18.0, 22.5],  # Sample optimized values

        }

        df = pd.DataFrame(data)
        df.to_csv(DATASET_PATH, index=False)
        print(f"✅ Created {DATASET_PATH} successfully with new cost-related columns!")
    else:
        print(f"✅ {DATASET_PATH} already exists!")

if __name__ == "__main__":
    create_initial_dataset()
