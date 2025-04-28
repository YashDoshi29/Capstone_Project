#data with indicators, calculated all stocks together

# # preprocessing_factors.py

# import pandas as pd
# import os
# import ta

# # Path to your combined CSV file
# combined_file = "data/combined_data.csv"

# # Load the CSV file
# df = pd.read_csv(combined_file)

# # Normalize column names to lowercase for consistency
# df.columns = [col.lower() for col in df.columns]

# # Check if a "date" column exists; if not, attempt to recover it from the index.
# if "date" not in df.columns:
#     print("Warning: 'date' column not found. Resetting index and using it as 'date'.")
#     df.reset_index(inplace=True)
#     if "index" in df.columns:
#         df.rename(columns={"index": "date"}, inplace=True)
#     else:
#         raise ValueError("Unable to locate a 'date' column. Please check your CSV file.")

# # Convert the "date" column to datetime
# df["date"] = pd.to_datetime(df["date"], errors="coerce")
# if df["date"].isnull().all():
#     raise ValueError("The 'date' column could not be parsed as dates. Please check the CSV file.")

# # Check for essential price columns: if "close" is not present but "adj close" is, use it.
# if "close" not in df.columns:
#     if "adj close" in df.columns:
#         df["close"] = df["adj close"]
#         print("Using 'adj close' as 'close'.")
#     else:
#         raise KeyError("Neither 'close' nor 'adj close' column found in the CSV.")

# # Ensure the other required columns are present; if not, throw an error.
# for col in ["open", "high", "low", "volume"]:
#     if col not in df.columns:
#         raise KeyError(f"Required column '{col}' not found in the CSV.")

# # Check if the "ticker" column exists
# if "ticker" in df.columns:
#     df.sort_values(by=["ticker", "date"], inplace=True)
# else:
#     print("Warning: 'ticker' column not found. Sorting data by 'date' only.")
#     df.sort_values(by=["date"], inplace=True)

# def calculate_indicators(group):
#     # Calculate 20-day Simple Moving Average (SMA) and Exponential Moving Average (EMA)
#     group["SMA20"] = group["close"].rolling(window=20).mean()
#     group["EMA20"] = group["close"].ewm(span=20, adjust=False).mean()

#     # Calculate 14-day Relative Strength Index (RSI)
#     group["RSI14"] = ta.momentum.RSIIndicator(close=group["close"], window=14).rsi()

#     # Calculate MACD, its signal line, and MACD difference (histogram)
#     macd = ta.trend.MACD(close=group["close"])
#     group["MACD"] = macd.macd()
#     group["MACD_signal"] = macd.macd_signal()
#     group["MACD_diff"] = macd.macd_diff()

#     # Calculate On Balance Volume (OBV)
#     group["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=group["close"], volume=group["volume"]).on_balance_volume()

#     # Calculate 20-day moving average for volume (as a volume trend indicator)
#     group["Volume_MA20"] = group["volume"].rolling(window=20).mean()

#     # Calculate 14-day Average True Range (ATR)
#     atr = ta.volatility.AverageTrueRange(high=group["high"], low=group["low"], close=group["close"], window=14)
#     group["ATR14"] = atr.average_true_range()

#     return group

# # Apply indicator calculations: if "ticker" column exists, group by ticker; otherwise, process whole dataset.
# if "ticker" in df.columns:
#     df_processed = df.groupby("ticker").apply(calculate_indicators)
# else:
#     df_processed = calculate_indicators(df)

# # Reset index (optional) and save the enriched dataset
# df_processed.reset_index(drop=True, inplace=True)
# os.makedirs("data/processed", exist_ok=True)
# output_file = "data/processed/combined_processed_data.csv"
# df_processed.to_csv(output_file, index=False)

# print(f"Processed dataset with technical indicators saved to {output_file}")

##################################################################################################################################
##################################################################################################################################


#calculated indicators for the companies separated file

# calculate_indicators_per_file.py

# import pandas as pd
# import os
# import glob
# import ta

# # Folders for raw and processed data
# RAW_DATA_DIR = "data/raw"
# PROCESSED_DATA_DIR = "data/processed"

# os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# # Grab all CSV files in the raw folder
# csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))

# for file in csv_files:
#     # Example: "AAPL.csv" -> ticker = "AAPL"
#     ticker = os.path.basename(file).split(".")[0]
#     print(f"Processing {ticker}...")

#     # 1. Read the CSV, skipping the first 3 rows so line 4 becomes row 0 of data.
#     #    Assign columns manually to match the snippet's format.
#     try:
#         df = pd.read_csv(
#             file,
#             skiprows=3,               # Skip the 3 header lines
#             header=None,              # We are manually naming columns
#             names=["Date", "Close", "High", "Low", "Open", "Volume"]
#         )
#     except Exception as e:
#         print(f"Error reading {file}: {e}")
#         continue

#     # 2. Convert columns to the appropriate dtypes
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#     # Drop rows where Date failed to parse
#     df.dropna(subset=["Date"], inplace=True)

#     # Convert numeric columns
#     for col in ["Close", "High", "Low", "Open", "Volume"]:
#         df[col] = pd.to_numeric(df[col], errors="coerce")

#     # Drop rows where any of these essential columns are missing
#     df.dropna(subset=["Close", "High", "Low", "Open", "Volume"], inplace=True)

#     # 3. Sort by Date just to ensure chronological order
#     df.sort_values(by="Date", inplace=True)

#     # 4. Calculate technical indicators
#     # 4a. SMA20 and EMA20
#     df["SMA20"] = df["Close"].rolling(window=20).mean()
#     df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

#     # 4b. RSI (14-day)
#     df["RSI14"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()

#     # 4c. MACD
#     macd = ta.trend.MACD(close=df["Close"])
#     df["MACD"] = macd.macd()
#     df["MACD_signal"] = macd.macd_signal()
#     df["MACD_diff"] = macd.macd_diff()

#     # 4d. On Balance Volume (OBV)
#     df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"]).on_balance_volume()

#     # 4e. 20-day volume moving average
#     df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()

#     # 4f. 14-day Average True Range (ATR)
#     atr = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14)
#     df["ATR14"] = atr.average_true_range()

#     # 5. Save the processed data back to a new CSV in data/processed
#     output_file = os.path.join(PROCESSED_DATA_DIR, f"{ticker}.csv")
#     df.to_csv(output_file, index=False)
#     print(f"Processed data for {ticker} saved to {output_file}")

# print("All files processed.")


##################################################################################################################################
##################################################################################################################################

#combined all the files after adding the indicators separately

# combine_processed_files.py

import pandas as pd
import os
import glob

# Folder where your processed CSVs are stored
PROCESSED_DATA_DIR = "data/processed"
# Output file for the combined dataset
OUTPUT_FILE = "data/final_combined_dataset.csv"

# Get a list of all CSV files in the processed data folder
csv_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "*.csv"))

all_dataframes = []
for file in csv_files:
    # Infer the ticker symbol from the filename (e.g., AAPL.csv -> "AAPL")
    ticker = os.path.basename(file).split(".")[0]
    # Read the CSV
    df = pd.read_csv(file)
    # Add a new column for the ticker
    df["ticker"] = ticker
    all_dataframes.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(all_dataframes, ignore_index=True)

# Save the combined DataFrame as a new CSV file
combined_df.to_csv(OUTPUT_FILE, index=False)
print(f"Combined dataset saved to {OUTPUT_FILE}")
