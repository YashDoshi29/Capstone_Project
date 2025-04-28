# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
# from datasets import load_dataset

# # Load your fine-tuning dataset from the JSONL file.
# dataset = load_dataset("json", data_files={"train": "data/finetune/finetune_dataset.jsonl"}, split="train")

# # Map the response ("Up"/"Down") to numeric labels.
# def map_labels(example):
#     example["label"] = 1 if example["response"].strip().lower() == "up" else 0
#     return example

# dataset = dataset.map(map_labels)
# # Remove the original response and rename "prompt" to "text" for the model's input.
# dataset = dataset.remove_columns(["response"])
# dataset = dataset.rename_column("prompt", "text")

# # Inspect one example.
# print(dataset[0])

# # Use a finance-focused model such as FinBERT.
# model_name = "ProsusAI/finbert"  # Replace with your chosen model if needed.

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# # Tokenize the dataset.
# def tokenize_function(example):
#     return tokenizer(example["text"], truncation=True, max_length=256)

# tokenized_dataset = dataset.map(tokenize_function, batched=True)

# # Use a data collator to pad inputs during batching.
# data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# training_args = TrainingArguments(
#     output_dir="./finetuned_finbert",
#     evaluation_strategy="no",
#     learning_rate=2e-5,
#     per_device_train_batch_size=8,
#     num_train_epochs=3,
#     weight_decay=0.01,
# )

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_dataset,
#     tokenizer=tokenizer,
#     data_collator=data_collator,
# )

# # Fine-tune the model.
# trainer.train()

# # Save the fine-tuned model and tokenizer.
# model.save_pretrained("./finetuned_finbert")
# tokenizer.save_pretrained("./finetuned_finbert")

# print("Fine-tuning complete. Model saved to ./finetuned_finbert")














# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
# from datasets import load_dataset
# import evaluate
# import numpy as np
# from transformers import TrainerCallback

# class CheckpointLogger(TrainerCallback):
#     def on_save(self, args, state, control, **kwargs):
#         print(f"Checkpoint saved at step {state.global_step} in {args.output_dir}")
#         return control

# # 1. Load the fine-tuning dataset from the JSONL file.
# dataset = load_dataset("json", data_files={"train": "data/finetune/finetune_dataset.jsonl"}, split="train")

# # 2. Map the response to a numeric label: 1 for "Up", 0 for "Down".
# def map_labels(example):
#     example["label"] = 1 if example["response"].strip().lower() == "up" else 0
#     return example

# dataset = dataset.map(map_labels)
# # Remove the original "response" field and rename "prompt" to "text" (the model's input)
# dataset = dataset.remove_columns(["response"])
# dataset = dataset.rename_column("prompt", "text")

# # 3. Split the dataset into training and evaluation sets.
# split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
# train_dataset = split_dataset["train"]
# eval_dataset = split_dataset["test"]

# # 4. Load the tokenizer and the FinBERT model.
# model_name = "ProsusAI/finbert"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(
#     model_name,
#     num_labels=2,
#     ignore_mismatched_sizes=True  # Reinitialize classification head for 2 labels.
# )

# # 5. Tokenize the datasets.
# def tokenize_function(example):
#     return tokenizer(example["text"], truncation=True, max_length=256)

# train_dataset = train_dataset.map(tokenize_function, batched=True)
# eval_dataset = eval_dataset.map(tokenize_function, batched=True)

# data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# # 6. Set up the evaluation metric (accuracy) using the evaluate library.
# metric = evaluate.load("accuracy")

# def compute_metrics(eval_pred):
#     logits, labels = eval_pred
#     predictions = np.argmax(logits, axis=-1)
#     return metric.compute(predictions=predictions, references=labels)

# # 7. Define training arguments with checkpoint saving.
# training_args = TrainingArguments(
#     output_dir="./finetuned_finbert",
#     evaluation_strategy="epoch",  # Evaluate at the end of each epoch.
#     save_strategy="steps",          # Save checkpoints at specified steps.
#     save_steps=1000,                # Save a checkpoint every 1000 steps.
#     save_total_limit=2,             # Keep only the latest 2 checkpoints.
#     learning_rate=2e-5,
#     per_device_train_batch_size=8,
#     per_device_eval_batch_size=8,
#     num_train_epochs=3,
#     weight_decay=0.01,
#     logging_dir="./logs",
#     logging_steps=100,
# )

# # 8. Initialize the Trainer.
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=eval_dataset,
#     tokenizer=tokenizer,
#     data_collator=data_collator,
#     compute_metrics=compute_metrics,
#     callbacks=[CheckpointLogger()]
# )

# # 9. Fine-tune the model.
# trainer.train()

# # 10. Evaluate the model on the evaluation set.
# eval_results = trainer.evaluate()
# print("Evaluation results:", eval_results)

# # 11. Save the final fine-tuned model.
# model.save_pretrained("/Users/nemi/finetuned_finbert")
# tokenizer.save_pretrained("/Users/nemi/finetuned_finbert")










import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange, BollingerBands
import os
from tqdm import tqdm

# Configuration
TICKERS = ['AAPL']  # Test with single ticker first
END_DATE = datetime.now() - timedelta(days=90)
START_DATE = END_DATE - timedelta(days=365*3)  # 3 years data

def fetch_stock_data(ticker):
    """Fetch stock data with proper format conversion"""
    try:
        df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
        if df.empty:
            print(f"No data for {ticker}")
            return None
            
        # Convert all numeric columns to float64
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        return df.dropna()
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

def calculate_indicators(df):
    """Calculate technical indicators with guaranteed 1D input"""
    try:
        indicators = pd.DataFrame(index=df.index)
        
        # Explicitly convert to Series with .values to ensure 1D
        close = pd.Series(df['Close'].values, index=df.index)
        high = pd.Series(df['High'].values, index=df.index)
        low = pd.Series(df['Low'].values, index=df.index)
        volume = pd.Series(df['Volume'].values, index=df.index)
        
        # Moving Averages
        indicators['SMA_20'] = close.rolling(20).mean()
        indicators['EMA_20'] = EMAIndicator(close=close, window=20).ema_indicator()
        
        # Momentum Indicators
        indicators['RSI_14'] = RSIIndicator(close=close, window=14).rsi()
        
        # MACD
        macd = MACD(close=close)
        indicators['MACD'] = macd.macd()
        indicators['MACD_Signal'] = macd.macd_signal()
        indicators['MACD_Hist'] = macd.macd_diff()
        
        # Volume Indicators
        indicators['OBV'] = OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()
        indicators['Volume_MA_20'] = volume.rolling(20).mean()
        
        # Volatility Indicators
        atr = AverageTrueRange(high=high, low=low, close=close, window=14)
        indicators['ATR_14'] = atr.average_true_range()
        
        bb = BollingerBands(close=close)
        indicators['BB_Upper'] = bb.bollinger_hband()
        indicators['BB_Mid'] = bb.bollinger_mavg()
        indicators['BB_Lower'] = bb.bollinger_lband()
        
        return indicators.dropna()
    except Exception as e:
        print(f"Indicator error for {df.index[0] if not df.empty else 'unknown'}: {str(e)}")
        return None

def create_labels(df, lookahead=5, threshold=0.02):
    """Create binary labels for classification"""
    future_prices = df['Close'].shift(-lookahead)
    price_change = (future_prices - df['Close']) / df['Close']
    return (price_change > threshold).astype(int)

def process_ticker(ticker):
    """Complete processing pipeline for a single ticker"""
    try:
        print(f"\nProcessing {ticker}...")
        df = fetch_stock_data(ticker)
        if df is None:
            return None
            
        indicators = calculate_indicators(df)
        if indicators is None:
            return None
            
        # Combine data
        combined = pd.concat([df, indicators], axis=1)
        
        # Create labels
        combined['target'] = create_labels(combined)
        
        # Clean data
        combined = combined.dropna()
        combined = combined.iloc[:-5]  # Remove last 5 days without future prices
        
        if len(combined) < 100:
            print(f"Insufficient data for {ticker} after processing")
            return None
            
        # Add ticker info
        combined['ticker'] = ticker
        combined = combined.reset_index()
        
        return combined
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def main():
    print("Starting pipeline...")
    all_data = []
    
    for ticker in tqdm(TICKERS):
        data = process_ticker(ticker)
        if data is not None:
            all_data.append(data)
            print(f"Successfully processed {ticker} with {len(data)} rows")
    
    if not all_data:
        print("\nNo data processed successfully")
        return
    
    # Combine and save data
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save processed data
    os.makedirs('data/processed', exist_ok=True)
    data_path = 'data/processed/final_dataset.csv'
    final_df.to_csv(data_path, index=False)
    print(f"\nSaved processed data to {data_path}")
    
    # Verify
    print("\nSample data:")
    print(final_df[['Date', 'ticker', 'Close', 'SMA_20', 'RSI_14', 'target']].head())

if __name__ == "__main__":
    main()