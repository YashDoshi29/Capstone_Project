# import os
# import requests
# import pandas as pd
# import random
# import torch
# from datetime import date, timedelta, datetime
# from torch.utils.data import Dataset
# import numpy as np
# from sklearn.metrics import accuracy_score

# # For fetching stock data
# import yfinance as yf

# # For using the FinBERT sentiment classifier
# from transformers import pipeline, BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# #######################################
# # Part 1: Fetching News Data from API
# #######################################

# # -----------------------------------------
# # Settings: API key, stock list, and dates
# # -----------------------------------------
# NEWS_API_KEY = "4c310cb414224d468ee9087dd9f208d6"  # <-- Replace with your actual NewsAPI key.
# stocks = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]
# page_size = 100  # Maximum articles per request

# # Define date ranges
# # Training period: January 1 to February 28, 2023
# train_from_date = date(2025, 1, 1)
# train_to_date = date(2025, 2, 28)
# # Test period: March 1 to March 31, 2023 (to be used for backtesting)
# test_from_date = date(2025, 3, 1)
# test_to_date = date(2025, 3, 31)

# def fetch_news_for_stock(stock, from_date, to_date, api_key):
#     """
#     Fetch news articles for a given stock symbol between from_date and to_date.
#     """
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": stock,
#         "from": str(from_date),
#         "to": str(to_date),
#         "sortBy": "publishedAt",
#         "language": "en",
#         "pageSize": page_size,
#         "apiKey": api_key,
#     }
#     response = requests.get(url, params=params)
#     data = response.json()
#     articles = data.get("articles", [])
#     records = []
#     for article in articles:
#         records.append({
#             "stock": stock,
#             "publishedAt": article.get("publishedAt"),
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "content": article.get("content")
#         })
#     return records

# # -------------------------------
# # Fetch and Save Training Data
# # -------------------------------
# train_articles = []
# print("Fetching training (Jan-Feb 2025) news...")
# for stock in stocks:
#     print(f"Fetching news for {stock} for training period...")
#     articles = fetch_news_for_stock(stock, train_from_date, train_to_date, NEWS_API_KEY)
#     train_articles.extend(articles)
# train_df = pd.DataFrame(train_articles)
# train_filename = "stock_news_train.csv"
# train_df.to_csv(train_filename, index=False)
# print(f"Training news data saved to {train_filename}")

# # -------------------------------
# # Fetch and Save Test Data
# # -------------------------------
# test_articles = []
# print("Fetching test (March 2025) news...")
# for stock in stocks:
#     print(f"Fetching news for {stock} for test period...")
#     articles = fetch_news_for_stock(stock, test_from_date, test_to_date, NEWS_API_KEY)
#     test_articles.extend(articles)
# test_df = pd.DataFrame(test_articles)
# test_filename = "stock_news_test.csv"
# test_df.to_csv(test_filename, index=False)
# print(f"Test news data saved to {test_filename}")

# ######################################################
# # Part 2: Enrich Data with Automatic Sentiment Labels
# ######################################################
# # The goal is to label each article using:
# #   (1) FinBERT's text-based sentiment prediction.
# #   (2) The corresponding stock's price change on the publication day.
# # We'll combine these signals using a simple heuristic.

# # ------------------------------
# # A. Preload Stock Price Data
# # ------------------------------
# # We fetch historical price data for all stocks over the entire range.
# # We'll cover from the earliest training date to one day after test period.
# min_date = train_from_date
# max_date = test_to_date + timedelta(days=1)
# all_stocks_price_data = {}
# for stock in stocks:
#     print(f"Fetching historical price data for {stock} ...")
#     ticker = yf.Ticker(stock)
#     df = ticker.history(start=min_date.isoformat(), end=max_date.isoformat())
#     # Ensure the DataFrame index is in YYYY-MM-DD string format.
#     df.index = pd.to_datetime(df.index).strftime("%Y-%m-%d")
#     all_stocks_price_data[stock] = df

# # ------------------------------
# # B. Initialize the FinBERT Pipeline for Sentiment Prediction
# # ------------------------------
# # We use the pretrained FinBERT model.
# finbert_pipeline = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", tokenizer="yiyanghkust/finbert-tone")

# # ------------------------------
# # C. Define Helper Functions for Labeling
# # ------------------------------
# threshold = 0.01  # 1% change threshold

# def get_price_sentiment(stock, publishedAt):
#     """
#     Given a stock ticker and the publishedAt string from the news article,
#     look up the historical price data and compute the price movement sentiment.
#     Returns:
#         price_sent: "positive", "negative", or "neutral", based on the percentage change.
#     """
#     try:
#         # Extract publication date (we take only the date part)
#         pub_date = pd.to_datetime(publishedAt).date()
#     except Exception as e:
#         return "neutral"
    
#     df = all_stocks_price_data.get(stock)
#     if df is None or df.empty:
#         return "neutral"
    
#     # Get list of trading days (as date objects)
#     trading_days = [pd.to_datetime(x).date() for x in df.index]
#     if pub_date in trading_days:
#         current_day = pub_date
#     else:
#         # If not a trading day, take the closest previous trading day
#         valid_days = [d for d in trading_days if d < pub_date]
#         if valid_days:
#             current_day = max(valid_days)
#         else:
#             return "neutral"
#     # Attempt to get current day's and previous day's closing price
#     try:
#         current_str = current_day.strftime("%Y-%m-%d")
#         current_close = df.loc[current_str]['Close']
#         # Find the index of current_day in trading_days
#         idx = trading_days.index(current_day)
#         if idx == 0:  # No previous trading day available
#             return "neutral"
#         previous_day = trading_days[idx - 1]
#         previous_str = previous_day.strftime("%Y-%m-%d")
#         previous_close = df.loc[previous_str]['Close']
#     except Exception as e:
#         return "neutral"
    
#     if previous_close == 0:
#         return "neutral"
#     pct_change = (current_close - previous_close) / previous_close
#     # Derive sentiment from price change:
#     if pct_change > threshold:
#         return "positive"
#     elif pct_change < -threshold:
#         return "negative"
#     else:
#         return "neutral"

# def assign_label(row):
#     """
#     Combine text sentiment from FinBERT with stock price change sentiment.
#     Uses the article's title and description for text sentiment.
#     If the price sentiment is significant and contradicts the text sentiment,
#     we override with the price sentiment.
#     """
#     stock = row.get("stock", "")
#     publishedAt = row.get("publishedAt", "")
    
#     # Combine title and description (if available)
#     title = row.get("title") if pd.notna(row.get("title")) else ""
#     description = row.get("description") if pd.notna(row.get("description")) else ""
#     text = title + " " + description
#     if not text.strip():
#         # If there is no text, return neutral
#         return "neutral"
    
#     # Use FinBERT to predict sentiment from text
#     try:
#         result = finbert_pipeline(text)
#         # FinBERT typically returns labels like "positive", "negative", or "neutral"
#         text_sentiment = result[0]['label'].lower()
#     except Exception as e:
#         text_sentiment = "neutral"
    
#     # Get stock price sentiment based on the article's published date
#     price_sentiment = get_price_sentiment(stock, publishedAt)
    
#     # Heuristic: if the price sentiment is not neutral and it disagrees with text sentiment,
#     # override the text sentiment.
#     if price_sentiment != "neutral" and price_sentiment != text_sentiment:
#         final_label = price_sentiment
#     else:
#         final_label = text_sentiment
#     return final_label

# # -----------------------------------
# # D. Apply Automatic Labeling to Datasets
# # -----------------------------------
# print("Assigning sentiment labels to training data...")
# train_df["label"] = train_df.apply(assign_label, axis=1)
# train_labeled_filename = "stock_news_train_labeled.csv"
# train_df.to_csv(train_labeled_filename, index=False)
# print(f"Labeled training data saved to {train_labeled_filename}")

# print("Assigning sentiment labels to test data...")
# test_df["label"] = test_df.apply(assign_label, axis=1)
# test_labeled_filename = "stock_news_test_labeled.csv"
# test_df.to_csv(test_labeled_filename, index=False)
# print(f"Labeled test data saved to {test_labeled_filename}")

# ####################################################
# # Part 3: Fine-Tuning FinBERT with the Labeled Dataset
# ####################################################

# # -----------------------------------
# # Create a Custom PyTorch Dataset
# # -----------------------------------
# # In this example, we use the article's title and description as input text.
# # The labels are the ones computed above.
# label2id = {"negative": 0, "neutral": 1, "positive": 2}
# id2label = {v: k for k, v in label2id.items()}

# class NewsDataset(Dataset):
#     def __init__(self, data, tokenizer, max_length=256):
#         self.data = data.reset_index(drop=True)
#         self.tokenizer = tokenizer
#         self.max_length = max_length
        
#     def __len__(self):
#         return len(self.data)
    
#     def __getitem__(self, idx):
#         row = self.data.iloc[idx]
#         title = row["title"] if pd.notna(row["title"]) else ""
#         description = row["description"] if pd.notna(row["description"]) else ""
#         text = title + " " + description
#         encoding = self.tokenizer(
#             text,
#             truncation=True,
#             padding="max_length",
#             max_length=self.max_length,
#             return_tensors="pt"
#         )
#         input_ids = encoding["input_ids"].squeeze()        # shape: (max_length,)
#         attention_mask = encoding["attention_mask"].squeeze()  # shape: (max_length,)
#         label = label2id.get(row["label"], 1)  # default to neutral if not found
#         return {
#             "input_ids": input_ids,
#             "attention_mask": attention_mask,
#             "labels": torch.tensor(label, dtype=torch.long)
#         }

# # -----------------------------------
# # Load Labeled DataFrames
# # -----------------------------------
# train_data = pd.read_csv(train_labeled_filename)
# test_data = pd.read_csv(test_labeled_filename)

# # -----------------------------------
# # Load the FinBERT Tokenizer and Model for Fine-Tuning
# # -----------------------------------
# model_name = "yiyanghkust/finbert-tone"
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# # Create Dataset objects
# train_dataset = NewsDataset(train_data, tokenizer, max_length=256)
# test_dataset = NewsDataset(test_data, tokenizer, max_length=256)

# # -----------------------------------
# # Define a Compute Metrics Function for Evaluation
# # -----------------------------------
# def compute_metrics(eval_pred):
#     logits, labels = eval_pred
#     predictions = np.argmax(logits, axis=-1)
#     acc = accuracy_score(labels, predictions)
#     return {"accuracy": acc}

# # -----------------------------------
# # Set Training Arguments and Initialize Trainer
# # -----------------------------------
# training_args = TrainingArguments(
#     output_dir="./finbert_finetuned",
#     num_train_epochs=3,
#     per_device_train_batch_size=8,
#     per_device_eval_batch_size=8,
#     learning_rate=5e-5,
#     logging_steps=100,
#     save_steps=500,
#     evaluation_strategy="steps",  # Evaluate during training
#     eval_steps=200,
#     save_total_limit=2,
#     logging_dir="./logs",
# )

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=test_dataset,
#     compute_metrics=compute_metrics,
# )

# # -------------------------
# # Fine-Tuning FinBERT
# # -------------------------
# print("Starting fine-tuning of FinBERT on the labeled news dataset...")
# trainer.train()

# print("Evaluating on the test dataset...")
# eval_results = trainer.evaluate()
# print(f"Test Evaluation Results: {eval_results}")

# # Save the fine-tuned model and tokenizer.
# model.save_pretrained("./finbert_finetuned")
# tokenizer.save_pretrained("./finbert_finetuned")
# print("FinBERT fine-tuning complete and model saved to ./finbert_finetuned")



#NEWS_API_KEY = "4c310cb414224d468ee9087dd9f208d6"  # <-- Replace with your actual NewsAPI key.

# import requests
# import pandas as pd
# from datetime import datetime
# from sklearn.model_selection import train_test_split

# # --------------------------------
# # Settings and API Key Setup
# # --------------------------------
# NEWS_API_KEY = "4c310cb414224d468ee9087dd9f208d6"  # Replace with your actual NewsAPI key.
# stocks = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# # --------------------------------
# # Define Date Range for Fetching Data
# # --------------------------------
# # Your plan permits articles as far back as 2025-03-07.
# # To avoid issues on the boundary, we start on 2025-03-08.
# # We fetch articles until the current date.
# start_date = datetime(2025, 3, 8)
# end_date = datetime.now()  # Current date

# def fetch_news(stock, from_date, to_date, api_key):
#     """
#     Fetch news articles for a given stock symbol between from_date and to_date.
#     Uses the "everything" endpoint with an enhanced financial query.
#     """
#     url = "https://newsapi.org/v2/everything"
#     # Enhance query by combining the stock ticker with financial-related keywords.
#     query = f'{stock} AND (stock OR shares OR "financial news" OR market)'
#     params = {
#         "q": query,
#         "from": from_date.strftime("%Y-%m-%d"),
#         "to": to_date.strftime("%Y-%m-%d"),
#         "sortBy": "publishedAt",
#         "language": "en",
#         "pageSize": 100,     # Maximum articles per request
#         "apiKey": api_key,
#     }
    
#     try:
#         response = requests.get(url, params=params)
#     except Exception as e:
#         print(f"Error fetching news for {stock}: {e}")
#         return []
    
#     if response.status_code != 200:
#         try:
#             error_message = response.json().get("message", "No error message provided.")
#         except Exception:
#             error_message = "No error message provided."
#         print(f"Error response for {stock}: {response.status_code} - {error_message}")
#         return []
    
#     try:
#         data = response.json()
#     except Exception as e:
#         print(f"Error decoding JSON for {stock}: {e}")
#         return []
    
#     if data.get("status") != "ok":
#         print(f"API returned error for {stock}: {data.get('message')}")
#         return []
    
#     articles = data.get("articles", [])
#     if not articles:
#         print(f"No articles found for {stock} between {from_date.strftime('%Y-%m-%d')} and {to_date.strftime('%Y-%m-%d')}.")
    
#     records = []
#     for article in articles:
#         records.append({
#             "stock": stock,
#             "publishedAt": article.get("publishedAt"),
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "content": article.get("content"),
#             "source": article.get("source", {}).get("name")
#         })
#     return records

# # --------------------------------
# # Fetch News for All Stocks
# # --------------------------------
# all_articles = []
# print(f"Fetching news data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...\n")
# for stock in stocks:
#     print(f"Fetching news for {stock}...")
#     articles = fetch_news(stock, start_date, end_date, NEWS_API_KEY)
#     print(f"  Found {len(articles)} articles for {stock}.")
#     all_articles.extend(articles)

# total_articles = len(all_articles)
# print(f"\nTotal articles fetched: {total_articles}.")

# if total_articles == 0:
#     raise ValueError("No articles were fetched. Please verify your API key, date range, and subscription limits.")

# # --------------------------------
# # Save All Fetched Data to a Master CSV
# # --------------------------------
# news_df = pd.DataFrame(all_articles)
# # Ensure that publishedAt is recognized as a datetime.
# news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'], errors='coerce')
# master_filename = "stock_news_master.csv"
# news_df.to_csv(master_filename, index=False)
# print(f"\nMaster news data saved to {master_filename} with {len(news_df)} records.")

# # --------------------------------
# # Split the Data into Train/Validation and Test Sets
# # --------------------------------
# # In this example, we split based on publication date.
# # Use articles published on or after 2025-04-01 as the test set (for backtesting).
# # The remainder (before 2025-04-01) goes to training + validation.
# split_date = pd.to_datetime("2025-04-01")

# test_df = news_df[news_df['publishedAt'] >= split_date]
# train_val_df = news_df[news_df['publishedAt'] < split_date]

# print(f"\nTotal records for training+validation: {len(train_val_df)}")
# print(f"Total records for test (backtesting): {len(test_df)}")

# # Further split training+validation into train and validation (e.g., 90% train, 10% validation)
# if len(train_val_df) > 0:
#     train_df, val_df = train_test_split(train_val_df, test_size=0.1, random_state=42)
# else:
#     train_df = train_val_df.copy()
#     val_df = pd.DataFrame()

# # Save splits as CSV files.
# train_filename = "stock_news_train.csv"
# val_filename = "stock_news_val.csv"
# test_filename = "stock_news_test.csv"

# train_df.to_csv(train_filename, index=False)
# val_df.to_csv(val_filename, index=False)
# test_df.to_csv(test_filename, index=False)

# print(f"\nSplit sizes:")
# print(f"  Training set: {len(train_df)} records saved to {train_filename}")
# print(f"  Validation set: {len(val_df)} records saved to {val_filename}")
# print(f"  Test set: {len(test_df)} records saved to {test_filename}")

# # --------------------------------
# # Display a Sample of the Fetched News Data
# # --------------------------------
# print("\nSample fetched news articles:")
# print(news_df.head())













import requests
import pandas as pd
import os
import time
from datetime import datetime
from sklearn.model_selection import train_test_split

# --------------------------------
# Settings and API Key Setup
# --------------------------------
NEWS_API_KEY = "4c310cb414224d468ee9087dd9f208d6"  # Replace with your actual NewsAPI key.
stocks = [
    'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
    'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
    'TSLA', 'F', 'COIN', 'MRNA'
]

# --------------------------------
# Define Date Range for Fetching Data
# --------------------------------
# Your plan permits articles as far back as 2025-03-07.
# To avoid issues on the boundary, we start on 2025-03-08.
# We fetch articles until the current date.
start_date = datetime(2025, 3, 11)
end_date = datetime.now()  # Current date

def fetch_news(stock, from_date, to_date, api_key):
    """
    Fetch news articles for a given stock symbol between from_date and to_date.
    Uses the "everything" endpoint with an enhanced financial query.
    """
    url = "https://newsapi.org/v2/everything"
    # Enhance query by combining the stock ticker with financial-related keywords.
    query = f'{stock} AND (stock OR shares OR "financial news" OR market)'
    params = {
        "q": query,
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 100,     # Maximum articles per request
        "apiKey": api_key,
    }
    
    try:
        response = requests.get(url, params=params)
    except Exception as e:
        print(f"Error fetching news for {stock}: {e}")
        return []
    
    if response.status_code != 200:
        try:
            error_message = response.json().get("message", "No error message provided.")
        except Exception:
            error_message = "No error message provided."
        print(f"Error response for {stock}: {response.status_code} - {error_message}")
        return []
    
    try:
        data = response.json()
    except Exception as e:
        print(f"Error decoding JSON for {stock}: {e}")
        return []
    
    if data.get("status") != "ok":
        print(f"API returned error for {stock}: {data.get('message')}")
        return []
    
    articles = data.get("articles", [])
    if not articles:
        print(f"No articles found for {stock} between {from_date.strftime('%Y-%m-%d')} and {to_date.strftime('%Y-%m-%d')}.")
    
    records = []
    for article in articles:
        records.append({
            "stock": stock,
            "publishedAt": article.get("publishedAt"),
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "source": article.get("source", {}).get("name")
        })
    return records

print(f"Fetching news data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...\n")

# --------------------------------
# Load Existing Master File (if available)
# --------------------------------
master_filename = "stock_news_master.csv"
if os.path.exists(master_filename):
    existing_df = pd.read_csv(master_filename)
    # Convert publishedAt to a timezone-aware datetime (UTC)
    existing_df['publishedAt'] = pd.to_datetime(existing_df['publishedAt'], errors='coerce', utc=True)
    print(f"Loaded existing master file with {len(existing_df)} records.")
else:
    existing_df = pd.DataFrame()

# --------------------------------
# Determine Stocks Needing to be Fetched
# --------------------------------
fetched_stocks = set(existing_df['stock'].unique()) if not existing_df.empty else set()
stocks_to_fetch = [s for s in stocks if s not in fetched_stocks]
print(f"Stocks already fetched: {fetched_stocks}")
print(f"Stocks to fetch news for: {stocks_to_fetch}")

# --------------------------------
# Fetch News for Stocks That Haven't Been Fetched Yet
# --------------------------------
for stock in stocks_to_fetch:
    print(f"Fetching news for {stock}...")
    articles = fetch_news(stock, start_date, end_date, NEWS_API_KEY)
    print(f"  Found {len(articles)} articles for {stock}.")
    if articles:
        new_df = pd.DataFrame(articles)
        # Convert publishedAt to UTC (tz-aware)
        new_df['publishedAt'] = pd.to_datetime(new_df['publishedAt'], errors='coerce', utc=True)
        existing_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        print(f"No new articles for {stock}.")
    time.sleep(1)  # Small delay to help with rate limiting

total_articles = len(existing_df)
print(f"\nTotal articles fetched (including previous data): {total_articles}.")

# --------------------------------
# Save Updated Master News File
# --------------------------------
existing_df.to_csv(master_filename, index=False)
print(f"\nMaster news data saved to {master_filename} with {total_articles} records.")

# --------------------------------
# Split the Data into Train/Validation and Test Sets
# --------------------------------
# Use articles published on or after 2025-04-01 as the test set (for backtesting).
# The remainder (before 2025-04-01) goes to training + validation.
split_date = pd.to_datetime("2025-04-01").tz_localize("UTC")
test_df = existing_df[existing_df['publishedAt'] >= split_date]
train_val_df = existing_df[existing_df['publishedAt'] < split_date]

print(f"\nTotal records for training+validation: {len(train_val_df)}")
print(f"Total records for test (backtesting): {len(test_df)}")

# Further split training+validation into train and validation (e.g., 90% train, 10% validation)
if len(train_val_df) > 0:
    train_df, val_df = train_test_split(train_val_df, test_size=0.1, random_state=42)
else:
    train_df = train_val_df.copy()
    val_df = pd.DataFrame()

train_filename = "stock_news_train.csv"
val_filename = "stock_news_val.csv"
test_filename = "stock_news_test.csv"

train_df.to_csv(train_filename, index=False)
val_df.to_csv(val_filename, index=False)
test_df.to_csv(test_filename, index=False)

print(f"\nSplit sizes:")
print(f"  Training set: {len(train_df)} records saved to {train_filename}")
print(f"  Validation set: {len(val_df)} records saved to {val_filename}")
print(f"  Test set: {len(test_df)} records saved to {test_filename}")

print("\nSample fetched news articles:")
print(existing_df.head())
