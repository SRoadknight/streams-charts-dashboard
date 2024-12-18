# src/utils/file_utils.py

import os
import pandas as pd

def load_data_from_csv(file_path):
    """Load data from a CSV file if it exists."""
    if os.path.exists(file_path):
        print(f"Loading data from {file_path}")
        return pd.read_csv(file_path)
    return None

def save_to_csv(file_path, df):
    """Save a DataFrame to a CSV file."""
    if df.empty:
        print("No data found. CSV not created.")
        return
    
    data_dir = os.path.dirname(file_path)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}.")