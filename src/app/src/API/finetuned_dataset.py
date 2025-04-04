import pandas as pd
import os
import json

# Load your processed dataset with low_memory disabled and parse the Date column.
df = pd.read_csv(
    "/Users/nemi/Documents/Capstone_Project/src/app/src/API/data/final_combined_dataset.csv",
    low_memory=False,
    parse_dates=["Date"]
)

# Drop rows where Date is missing
df = df.dropna(subset=["Date"])

# Sort by ticker and Date to correctly compute next day's price for each stock.
df.sort_values(by=["ticker", "Date"], inplace=True)

# For each ticker, compute a target: if the next day's Close > today's Close then label "Up", else "Down".
def compute_target(group):
    group = group.copy()
    group["target"] = (group["Close"].shift(-1) > group["Close"]).astype(int)  # 1 means Up, 0 means Down
    group["label"] = group["target"].map({1: "Up", 0: "Down"})
    return group

# Using group_keys=False avoids carrying the group key in the index.
df = df.groupby("ticker", group_keys=False).apply(compute_target).reset_index(drop=True)

# Drop rows where target is NaN (usually the last row for each ticker)
df = df.dropna(subset=["target"])

# Create the fine-tuning dataset: for each row, create a prompt and a response.
os.makedirs("data/finetune", exist_ok=True)
output_path = "data/finetune/finetune_dataset.jsonl"

with open(output_path, "w") as f:
    for idx, row in df.iterrows():
        # Format the Date safely because we've dropped NaT rows.
        date_str = row["Date"].strftime('%Y-%m-%d')
        prompt = (
            f"Stock: {row['ticker']}, Date: {date_str}, "
            f"Close: {row['Close']:.2f}, SMA20: {row['SMA20']:.2f}, EMA20: {row['EMA20']:.2f}, "
            f"RSI14: {row['RSI14']:.2f}, MACD: {row['MACD']:.2f}, OBV: {row['OBV']:.0f}, "
            f"ATR14: {row['ATR14']:.2f}. Predict if tomorrow's price will go Up or Down:"
        )
        response = row["label"]
        f.write(json.dumps({"prompt": prompt, "response": response}) + "\n")

print(f"Finetuning dataset saved to {output_path}")
