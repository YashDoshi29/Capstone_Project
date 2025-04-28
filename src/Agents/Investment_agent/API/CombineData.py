# combine_csv.py

import pandas as pd
import glob
import os

# Define the directory containing raw CSV files and the output file path
raw_data_dir = "data/raw"
output_file = "data/combined_data.csv"

# Get a list of all CSV files in the raw data directory
csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))

# Initialize an empty list to store individual DataFrames
dataframes = []

for file in csv_files:
    # Extract ticker symbol from filename (e.g., "AAPL.csv" -> "AAPL")
    ticker = os.path.basename(file).split(".")[0]
    # Read CSV file; parse dates if your CSV has a date column
    df = pd.read_csv(file, index_col=0, parse_dates=True)
    # Add a new column for the ticker symbol
    df["ticker"] = ticker
    dataframes.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(dataframes)

# Optional: Reset index if you want a "date" column instead of using the current index
combined_df.reset_index(inplace=True)
combined_df = combined_df.rename(columns={"index": "date"})

# Save the combined DataFrame as a new CSV file
combined_df.to_csv(output_file, index=False)
print(f"Combined CSV file saved to {output_file}")
