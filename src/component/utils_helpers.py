import os
import pandas as pd

def save_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        print(f"{filename} not found.")
        return None
