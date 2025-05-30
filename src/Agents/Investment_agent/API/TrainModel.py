# #FINAL CODE FOR FETCHING DATA FROM SCRATCH TO FINAL FINETUNE DATA - APRIL 10

############################################
# PART 1 (UPDATED): FETCH 2015–2024 INTO data/raw/
############################################
# import os
# import pandas as pd
# import yfinance as yf

# # 20 tickers
# STOCK_LIST = [
#     'AAPL','MSFT','NVDA','AMD','JNJ','PFE','JPM','GS',
#     'KO','PEP','XOM','NEE','CVX','WMT','HD','GME',
#     'TSLA','F','COIN','MRNA'
# ]

# # This folder already contains your raw CSVs (previously 4 yr slices).
# RAW_DATA_DIR = "data/raw"
# os.makedirs(RAW_DATA_DIR, exist_ok=True)

# # === explicit time range ===
# START_DATE = "2015-01-01"   # inclusive → Jan 1, 2015
# END_DATE   = "2025-01-01"   # exclusive → so up through Dec 31, 2024

# def fetch_and_overwrite():
#     for sym in STOCK_LIST:
#         out_path = os.path.join(RAW_DATA_DIR, f"{sym}.csv")
#         print(f"\n→ Fetching {sym} from {START_DATE} to {END_DATE}…")

#         # download the full range
#         df = yf.download(
#             sym,
#             start=START_DATE,
#             end=END_DATE,
#             progress=False,
#             auto_adjust=True
#         )
#         if df is None or df.empty:
#             print(f"[ERROR] No data for {sym}.csv; skipping.")
#             continue

#         # ensure index name matches your existing files
#         df.index.name = "Date"

#         # overwrite the raw CSV
#         df.to_csv(out_path)
#         print(f"[OK] Wrote {len(df)} rows to {out_path}")

# if __name__ == "__main__":
#     fetch_and_overwrite()


# # ############################################
# # # PART 2: PROCESSING RAW DATA & COMPUTING TECHNICAL INDICATORS
# # ############################################
# import glob
# import ta

# # Directory for processed files
# PROCESSED_DATA_DIR = "data/processed"
# os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# def process_stock_csv(file_path):
#     """
#     Read a raw CSV file, rename columns to standard names,
#     parse the Date column, compute technical indicators, and label data.
#     """
#     print(f"Processing file: {file_path}...")
    
#     # Read the CSV without any special arguments since our files are not in standard format.
#     # (They come with headers like "Price Ticker, Close AAPL, High AAPL, ..." etc.)
#     df = pd.read_csv(file_path, header=0)
    
#     # Strip spaces from column names
#     df.columns = df.columns.str.strip()
    
#     # Rename columns using regex:
#     # Assume that the first column (which might be labeled as "Price Ticker" or something similar) is the date.
#     # Then any column starting with "Close" becomes "Close", "High" becomes "High", etc.
#     df.columns = df.columns.str.replace(r'^Price.*', 'Date', regex=True)
#     df.columns = df.columns.str.replace(r'^Close.*', 'Close', regex=True)
#     df.columns = df.columns.str.replace(r'^High.*', 'High', regex=True)
#     df.columns = df.columns.str.replace(r'^Low.*', 'Low', regex=True)
#     df.columns = df.columns.str.replace(r'^Open.*', 'Open', regex=True)
#     df.columns = df.columns.str.replace(r'^Volume.*', 'Volume', regex=True)
    
#     # Debug: print renamed columns.
#     print("Renamed columns:", df.columns.tolist())
    
#     # Ensure we have a Date column
#     if "Date" not in df.columns:
#         print("No 'Date' column found. Exiting processing for this file.")
#         return None
    
#     # Convert the Date column to datetime.
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#     df.dropna(subset=["Date"], inplace=True)
    
#     # Sort by Date
#     df.sort_values("Date", inplace=True)
    
#     # Convert other key columns to numeric (if needed)
#     for col in ["Close", "High", "Low", "Open", "Volume"]:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#     df.dropna(subset=["Close", "High", "Low", "Open", "Volume"], inplace=True)
    
#     # Calculate technical indicators.
#     df["SMA20"] = df["Close"].rolling(window=20).mean()
#     df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
#     df["RSI14"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    
#     macd = ta.trend.MACD(close=df["Close"])
#     df["MACD"] = macd.macd()
#     df["MACD_signal"] = macd.macd_signal()
#     df["MACD_diff"] = macd.macd_diff()
    
#     df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"]).on_balance_volume()
#     df["ATR14"] = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14).average_true_range()
    
#     # Label the data: if the next day’s Close > today’s, label as "Up", otherwise "Down"
#     df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
#     df["label"] = df["target"].map({1: "Up", 0: "Down"})
#     df = df.dropna(subset=["target"])  # drop the last row (no next day)
    
#     return df

# def process_all_raw():
#     raw_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
#     for file_path in raw_files:
#         df_processed = process_stock_csv(file_path)
#         if df_processed is None or df_processed.empty:
#             print(f"Skipping file: {file_path}")
#             continue
#         symbol = os.path.splitext(os.path.basename(file_path))[0]
#         output_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_processed.csv")
#         df_processed.to_csv(output_file, index=False)
#         print(f"Processed data for {symbol} saved to {output_file}")

# if __name__ == "__main__":
#     process_all_raw()

# ############################################
# # PART 3: COMBINING PROCESSED DATA INTO FINAL DATASET
# ############################################
# import glob

# FINAL_OUTPUT_FILE = "data/final_combined_dataset.csv"
# processed_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "*_processed.csv"))
# data_frames = []

# for file in processed_files:
#     symbol = os.path.basename(file).split("_")[0]
#     df = pd.read_csv(file, parse_dates=["Date"])
#     df["ticker"] = symbol  # add a ticker column for clarity
#     data_frames.append(df)

# if data_frames:
#     combined_df = pd.concat(data_frames, ignore_index=True)
#     combined_df.to_csv(FINAL_OUTPUT_FILE, index=False)
#     print(f"Final combined dataset saved to {FINAL_OUTPUT_FILE}")
# else:
#     print("No processed files to combine.")

# ############################################
# # PART 4: CREATING A FINETUNING DATASET FROM THE FINAL DATASET
# ############################################
# import json

# # Load the combined dataset.
# FINAL_DATASET_FILE = FINAL_OUTPUT_FILE
# df = pd.read_csv(FINAL_DATASET_FILE, low_memory=False, parse_dates=True)

# # Debug: list available columns.
# print("Columns in final dataset:", df.columns.tolist())

# # Ensure we have a Date column (check case-insensitively).
# if "Date" not in df.columns:
#     found_date = False
#     for col in df.columns:
#         if col.lower() == "date":
#             df = df.rename(columns={col: "Date"})
#             found_date = True
#             print(f"Renamed column '{col}' to 'Date'.")
#             break
#     if not found_date:
#         first_col = df.columns[0]
#         print(f"No 'Date' column found; assuming first column '{first_col}' contains date values and renaming it to 'Date'.")
#         df = df.rename(columns={first_col: "Date"})

# if "Date" not in df.columns:
#     raise KeyError("No 'Date' column found even after renaming.")

# # Drop rows with missing Date values.
# df = df.dropna(subset=["Date"])

# # Convert Date column to datetime and drop rows that cannot be parsed.
# df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
# df = df.dropna(subset=["Date"])

# # Ensure we have a 'ticker' column.
# if "ticker" not in df.columns:
#     raise KeyError("No 'ticker' column found in the dataset.")

# # Sort data by ticker and Date.
# df.sort_values(by=["ticker", "Date"], inplace=True)

# # Group by ticker and compute the target: if next day's Close > today's Close, label as "Up"
# def compute_target(group):
#     group = group.copy()
#     group["target"] = (group["Close"].shift(-1) > group["Close"]).astype(int)
#     group["label"] = group["target"].map({1: "Up", 0: "Down"})
#     return group

# df = df.groupby("ticker", group_keys=False).apply(compute_target).reset_index(drop=True)
# df = df.dropna(subset=["target"])  # drop last row for each ticker

# # Create directory for the fine-tuning dataset.
# os.makedirs("data/finetune", exist_ok=True)
# finetune_output_file = "data/finetune/finetune_dataset.jsonl"

# # Build and save prompt-response pairs.
# with open(finetune_output_file, "w") as f:
#     for idx, row in df.iterrows():
#         date_str = row["Date"].strftime("%Y-%m-%d")
#         prompt = (
#             f"Stock: {row['ticker']}, Date: {date_str}, Close: {row['Close']:.2f}, "
#             f"SMA20: {row['SMA20']:.2f}, EMA20: {row['EMA20']:.2f}, RSI14: {row['RSI14']:.2f}, "
#             f"MACD: {row['MACD']:.2f}, OBV: {row['OBV']:.0f}, ATR14: {row['ATR14']:.2f}. "
#             "Predict if tomorrow's price will go Up or Down:"
#         )
#         response = row["label"]
#         json_line = json.dumps({"prompt": prompt, "response": response})
#         f.write(json_line + "\n")

# print(f"Finetuning dataset saved to {finetune_output_file}")





#DATASET SPLIT - TRAIN, VALIDATION, TEST

# import json
# import pandas as pd
# import os
# from sklearn.model_selection import train_test_split

# # Path to your fine-tuning dataset JSONL file.
# INPUT_FILE = "data/finetune/finetune_dataset.jsonl"

# # Load all examples from the JSONL file into a DataFrame.
# data = []
# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     for line in f:
#         data.append(json.loads(line))
# df = pd.DataFrame(data)
# print("Total examples in dataset:", len(df))

# # Perform a three-way split: 70% Train, 15% Validation, 15% Test.
# # First, split off the test set.
# train_val_df, test_df = train_test_split(df, test_size=0.15, random_state=42, shuffle=True)
# # Then split the remaining train_val into train and validation.
# # To get approximately 70% train and 15% val overall, use test_size = 0.1765 (0.1765 * 0.85 ≈ 0.15).
# train_df, val_df = train_test_split(train_val_df, test_size=0.1765, random_state=42, shuffle=True)

# print("Training set size:", len(train_df))
# print("Validation set size:", len(val_df))
# print("Test set size:", len(test_df))

# # Create a directory to save the splits.
# os.makedirs("data/finetune/splits", exist_ok=True)

# def save_jsonl(df, filename):
#     with open(filename, "w", encoding="utf-8") as f:
#         for _, row in df.iterrows():
#             f.write(json.dumps(row.to_dict()) + "\n")

# # Save splits to separate JSONL files.
# save_jsonl(train_df, "data/finetune/splits/train.jsonl")
# save_jsonl(val_df, "data/finetune/splits/val.jsonl")
# save_jsonl(test_df, "data/finetune/splits/test.jsonl")

# print("Splits saved to data/finetune/splits/")





#Train test split with stratify


import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split

# ─── CONFIG ───────────────────────────────────────────────────────────────
INPUT_FILE  = "data/finetune/finetune_dataset.jsonl"
SPLITS_DIR  = "data/finetune/splits"
TRAIN_FILE  = os.path.join(SPLITS_DIR, "train_balanced_df.jsonl")
VAL_FILE    = os.path.join(SPLITS_DIR, "val_df.jsonl")
TEST_FILE   = os.path.join(SPLITS_DIR, "test_df.jsonl")

os.makedirs(SPLITS_DIR, exist_ok=True)

# ─── 1) LOAD JSONL INTO DATAFRAME ─────────────────────────────────────────
records = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))
df = pd.DataFrame(records)
print("Total examples:", len(df))
print("Overall balance:\n", df["response"].value_counts(normalize=True), "\n")

# ─── 2) STRATIFIED SPLIT 70/15/15 ──────────────────────────────────────────
# First carve off 15% for test
train_val_df, test_df = train_test_split(
    df,
    test_size=0.15,
    random_state=42,
    shuffle=True,
    stratify=df["response"]
)

# Then carve validation (≈0.1765 of train_val → 15% overall)
train_df, val_df = train_test_split(
    train_val_df,
    test_size=0.1765,
    random_state=42,
    shuffle=True,
    stratify=train_val_df["response"]
)

# assume train_df has a column "response" with values "Up"/"Down"
counts = train_df['response'].value_counts()
max_count = counts.max()

# collect each class, oversample the smaller one
dfs = []
for label, cnt in counts.items():
    df_label = train_df[train_df['response'] == label]
    if cnt < max_count:
        # sample with replacement to reach max_count
        df_label = pd.concat([
            df_label,
            df_label.sample(max_count - cnt, replace=True, random_state=42)
        ], ignore_index=True)
    dfs.append(df_label)

# concatenate and shuffle
train_balanced_df = pd.concat(dfs, ignore_index=True)
train_balanced_df = train_balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

print("After oversampling, train class balance:")
print(train_balanced_df['response'].value_counts())


print("Train size (after oversampling):", len(train_balanced_df),
      "balance:", train_balanced_df["response"].value_counts(normalize=True).to_dict())
print("Val   size:", len(val_df),    "balance:", val_df["response"].value_counts(normalize=True).to_dict())
print("Test  size:", len(test_df),   "balance:", test_df["response"].value_counts(normalize=True).to_dict())

# ─── 3) SAVE SPLITS AS JSONL ───────────────────────────────────────────────
def save_jsonl(df, path):
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row.to_dict()) + "\n")

save_jsonl(train_balanced_df, TRAIN_FILE)
save_jsonl(val_df,   VAL_FILE)
save_jsonl(test_df,  TEST_FILE)

# print(f"\nSplits written to {SPLITS_DIR}:")
# print(f"  • {TRAIN_FILE}")
# print(f"  • {VAL_FILE}")
# print(f"  • {TEST_FILE}")
