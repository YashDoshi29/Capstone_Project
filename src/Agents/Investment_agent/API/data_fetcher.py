# data_fetcher.py

# import yfinance as yf
# import pandas as pd
# import os
# from config import STOCK_LIST, START_DATE, END_DATE

# def fetch_stock_data(symbol):
#     """
#     Fetch historical daily stock data from Yahoo Finance for the given symbol.
#     """
#     try:
#         df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
#     except Exception as e:
#         print(f"Error fetching data for {symbol}: {e}")
#         return None

#     if df.empty:
#         print(f"No data returned for {symbol}.")
#         return None
#     return df

# def save_raw_data():
#     """
#     Fetch data for each stock in STOCK_LIST and save as CSV in data/raw.
#     """
#     os.makedirs("data/raw", exist_ok=True)
#     for symbol in STOCK_LIST:
#         print(f"Fetching data for {symbol}...")
#         df = fetch_stock_data(symbol)
#         if df is not None:
#             file_path = f"data/raw/{symbol}.csv"
#             df.to_csv(file_path)
#             print(f"Saved data for {symbol} to {file_path}")
#         else:
#             print(f"Failed to fetch data for {symbol}.")

# if __name__ == "__main__":
#     save_raw_data()





# combine_csv.py

# import pandas as pd
# import glob
# import os

# # Define the directory containing raw CSV files and the output file path
# raw_data_dir = "data/raw"
# output_file = "data/combined_data.csv"

# # Get a list of all CSV files in the raw data directory
# csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))

# # Initialize an empty list to store individual DataFrames
# dataframes = []

# for file in csv_files:
#     # Extract ticker symbol from filename (e.g., "AAPL.csv" -> "AAPL")
#     ticker = os.path.basename(file).split(".")[0]
#     # Read CSV file; parse dates if your CSV has a date column
#     df = pd.read_csv(file, index_col=0, parse_dates=True)
#     # Add a new column for the ticker symbol
#     df["ticker"] = ticker
#     dataframes.append(df)

# # Concatenate all DataFrames into one
# combined_df = pd.concat(dataframes)

# # Optional: Reset index if you want a "date" column instead of using the current index
# combined_df.reset_index(inplace=True)
# combined_df = combined_df.rename(columns={"index": "date"})

# # Save the combined DataFrame as a new CSV file
# combined_df.to_csv(output_file, index=False)
# print(f"Combined CSV file saved to {output_file}")







#new code with proper test split

import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange, BollingerBands
import json
from tqdm import tqdm

# Configuration
TICKERS = ['AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
           'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
           'TSLA', 'F', 'COIN', 'MRNA']

# Define time range: past 10 years for backtesting;
# Last 3 months are excluded from the end_date.
END_DATE = datetime.now() - timedelta(days=90)
START_DATE = END_DATE - timedelta(days=365*10)  # 10 years data

def fetch_stock_data(ticker):
    """Robust stock data fetcher with error handling"""
    try:
        df = yf.download(ticker, start=START_DATE.strftime("%Y-%m-%d"), end=END_DATE.strftime("%Y-%m-%d"), progress=False)
        if df.empty:
            print(f"No data for {ticker}")
            return None
        
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            print(f"Missing columns for {ticker}")
            return None
            
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

def calculate_indicators(df):
    """Calculate all technical indicators with proper data handling"""
    try:
        # Convert to float64 and ensure 1D arrays using .squeeze()
        close = df['Close'].astype('float64').values.squeeze()
        high = df['High'].astype('float64').values.squeeze()
        low = df['Low'].astype('float64').values.squeeze()
        volume = df['Volume'].astype('float64').values.squeeze()
        
        # Create a DataFrame to hold indicators
        indicators = pd.DataFrame(index=df.index)
        
        # Moving Averages
        indicators['SMA_20'] = pd.Series(close).rolling(window=20).mean()
        indicators['EMA_20'] = EMAIndicator(close=pd.Series(close), window=20).ema_indicator()
        
        # Momentum Indicator: RSI
        indicators['RSI_14'] = RSIIndicator(close=pd.Series(close), window=14).rsi()
        
        # MACD
        macd = MACD(close=pd.Series(close))
        indicators['MACD'] = macd.macd()
        indicators['MACD_Signal'] = macd.macd_signal()
        indicators['MACD_Hist'] = macd.macd_diff()
        
        # Volume Indicators
        indicators['OBV'] = OnBalanceVolumeIndicator(close=pd.Series(close), volume=pd.Series(volume)).on_balance_volume()
        indicators['Volume_MA_20'] = pd.Series(volume).rolling(20).mean()
        
        # Volatility Indicators
        atr = AverageTrueRange(
            high=pd.Series(high),
            low=pd.Series(low),
            close=pd.Series(close),
            window=14
        )
        indicators['ATR_14'] = atr.average_true_range()
        
        # Bollinger Bands (optional)
        bb = BollingerBands(close=pd.Series(close))
        indicators['BB_Upper'] = bb.bollinger_hband()
        indicators['BB_Mid'] = bb.bollinger_mavg()
        indicators['BB_Lower'] = bb.bollinger_lband()
        
        return indicators
    except Exception as e:
        print(f"Indicator error: {str(e)}")
        return None

def create_labels(df, lookahead=5, threshold=0.02):
    """Create meaningful labels for classification"""
    future_prices = df['Close'].shift(-lookahead)
    price_change = (future_prices - df['Close']) / df['Close']
    labels = (price_change > threshold).astype(int)
    return labels

def process_ticker(ticker):
    """Complete processing pipeline for a single ticker"""
    try:
        # Fetch data
        df = fetch_stock_data(ticker)
        if df is None:
            return None
        
        # Calculate indicators
        indicators = calculate_indicators(df)
        if indicators is None:
            return None
            
        # Combine original data with indicators
        df = pd.concat([df, indicators], axis=1)
        
        # Create labels
        df['Label'] = create_labels(df)
        
        # Clean data: drop missing values and remove last 5 days (unable to calculate future returns)
        df = df.dropna()
        df = df.iloc[:-5]
        
        if len(df) < 100:  # Minimum data requirement for further processing
            return None
            
        # Add ticker info and reset index
        df['Ticker'] = ticker
        df.reset_index(inplace=True)
        
        return df
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def create_finetuning_data(df, output_path):
    """Create JSONL format for finetuning"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        for _, row in df.iterrows():
            prompt = (
                f"Stock: {row['Ticker']}, Date: {row['Date'].strftime('%Y-%m-%d')}, "
                f"Close: {row['Close']:.2f}, SMA20: {row['SMA_20']:.2f}, "
                f"RSI14: {row['RSI_14']:.2f}, MACD: {row['MACD']:.2f}, "
                f"Volume: {row['Volume']:.0f}, ATR14: {row['ATR_14']:.2f}. "
                "Predict if price will go Up or Down:"
            )
            response = "Up" if row['Label'] == 1 else "Down"
            f.write(json.dumps({"prompt": prompt, "response": response}) + '\n')

def main():
    print("Starting pipeline...")
    all_data = []
    
    # Process each ticker
    for ticker in tqdm(TICKERS, desc="Processing Tickers"):
        data = process_ticker(ticker)
        if data is not None:
            all_data.append(data)
    
    if not all_data:
        print("No data processed successfully")
        return
    
    # Combine all dataframes
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save the processed combined dataset
    os.makedirs('data/processed', exist_ok=True)
    data_path = 'data/processed/final_dataset.csv'
    final_df.to_csv(data_path, index=False)
    print(f"Saved processed data to {data_path}")
    
    # Create finetuning dataset file
    finetune_path = 'data/finetune/finetune_data.jsonl'
    create_finetuning_data(final_df, finetune_path)
    print(f"Saved finetuning data to {finetune_path}")
    
    # Show a sample finetuning entry
    print("\nSample finetuning entry:")
    with open(finetune_path, 'r') as f:
        print(f.readline())

if __name__ == "__main__":
    main()
