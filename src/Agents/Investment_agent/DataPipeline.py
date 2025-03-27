import os
import time
import json
import requests
import numpy as np
import faiss
from datasets import Dataset, load_from_disk
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import yfinance as yf
from yahoo_fin import stock_info as si
from rapidfuzz import process, fuzz


# --- API Keys ---
ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'
NEWS_API_KEY = '4c310cb414224d468ee9087dd9f208d6'  # Replace with your actual key

# --- Alpha Vantage: Historical Stock Data_Synthesizer ---
def fetch_stock_data(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching stock data for {symbol}: {response.status_code}")
        return None

def preprocess_stock_data(stock_data):
    if not stock_data:
        return []
    time_series = stock_data.get('Time Series (Daily)', {})
    if not time_series:
        print("No time series data found.")
        return []
    documents = []
    for date, data in time_series.items():
        open_price = data.get('1. open', 'N/A')
        high_price = data.get('2. high', 'N/A')
        low_price = data.get('3. low', 'N/A')
        close_price = data.get('4. close', 'N/A')
        volume = data.get('5. volume', 'N/A')
        document = (
            f"Stock Data_Synthesizer - Date: {date}, Open: {open_price}, High: {high_price}, "
            f"Low: {low_price}, Close: {close_price}, Volume: {volume}"
        )
        documents.append(document)
    return documents

# --- Alpha Vantage: Technical Indicator (SMA) ---
def fetch_sma_data(symbol, interval="daily", time_period=50, series_type="close"):
    url = "https://www.alphavantage.co/query"
    params = {
         "function": "SMA",
         "symbol": symbol,
         "interval": interval,
         "time_period": time_period,
         "series_type": series_type,
         "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
         return response.json()
    else:
         print(f"Error fetching SMA data for {symbol}: {response.status_code}")
         return None

def preprocess_sma_data(sma_data):
    if not sma_data:
         return []
    sma_dict = sma_data.get("Technical Analysis: SMA", {})
    documents = []
    for date, data in sma_dict.items():
         sma_value = data.get("SMA", "N/A")
         document = f"SMA - Date: {date}, SMA: {sma_value}"
         documents.append(document)
    return documents

# --- Alpha Vantage: Fundamental Data_Synthesizer (Overview) ---
def fetch_fundamental_data(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
         "function": "OVERVIEW",
         "symbol": symbol,
         "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
         return response.json()
    else:
         print(f"Error fetching fundamental data for {symbol}: {response.status_code}")
         return None

def preprocess_fundamental_data(fund_data):
    if not fund_data or "Name" not in fund_data:
         return []
    # Select some key fundamentals (you can add more fields as needed)
    company_name = fund_data.get("Name", "N/A")
    market_cap = fund_data.get("MarketCapitalization", "N/A")
    pe_ratio = fund_data.get("PERatio", "N/A")
    document = f"Fundamental Data_Synthesizer - Company: {company_name}, MarketCap: {market_cap}, P/E Ratio: {pe_ratio}"
    return [document]

# --- Financial News Data_Synthesizer Functions ---
def fetch_financial_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 5
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
         return response.json()
    else:
         print(f"Error fetching news: {response.status_code}")
         return None

def preprocess_news_data(news_data):
    if not news_data:
         return []
    articles = news_data.get('articles', [])
    documents = []
    for article in articles:
         title = article.get('title', '')
         description = article.get('description', '')
         content = article.get('content', '')
         published_at = article.get('publishedAt', '')
         document = (
             f"News Article - Date: {published_at}, Title: {title}, "
             f"Description: {description}, Content: {content}"
         )
         documents.append(document)
    return documents

# --- Yahoo Finance Data_Synthesizer Functions ---
def fetch_yahoo_finance_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y", interval="1d")
    documents = []
    for date, row in hist.iterrows():
        doc = f"Yahoo Finance Data_Synthesizer - Date: {date.date()}, Open: {row['Open']}, High: {row['High']}, Low: {row['Low']}, Close: {row['Close']}, Volume: {row['Volume']}"
        documents.append(doc)
    return documents

# --- Combine All Data_Synthesizer ---
def preprocess_and_combine(symbol):
    # Fetch from Alpha Vantage
    stock_data = fetch_stock_data(symbol)
    docs_alpha = preprocess_stock_data(stock_data)
    
    sma_data = fetch_sma_data(symbol)
    docs_sma = preprocess_sma_data(sma_data)
    
    fund_data = fetch_fundamental_data(symbol)
    docs_fund = preprocess_fundamental_data(fund_data)
    
    # Fetch from Yahoo Finance
    docs_yahoo = fetch_yahoo_finance_data(symbol)
    
    # Fetch Financial News
    news_data = fetch_financial_news()
    docs_news = preprocess_news_data(news_data)
    
    # Combine documents from all sources
    all_documents = docs_alpha + docs_sma + docs_fund + docs_yahoo + docs_news
    return all_documents

# --- Build FAISS Index with TF-IDF (for internal retrieval) ---
def build_faiss_index(documents):
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(documents).toarray()
    X = np.float32(X)
    index = faiss.IndexFlatL2(X.shape[1])
    index.add(X)
    return index, vectorizer

# --- Save and View Dataset ---
def save_dataset(documents, dataset_path):
    # Create titles using the first few words of each document
    titles = [doc.split(',')[0] for doc in documents]
    dataset = Dataset.from_dict({
        "title": titles,
        "text": documents,
    })
    dataset.save_to_disk(dataset_path)
    print("Dataset saved to:", dataset_path)
    return dataset

def add_embeddings_to_dataset(dataset):
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    def compute_embedding(example):
        full_text = f"{example['title']} {example['text']}"
        embedding = embedder.encode(full_text).tolist()
        return {"embeddings": embedding}
    dataset = dataset.map(compute_embedding)
    dataset = dataset.add_faiss_index(column="embeddings")
    return dataset

# --- Main Execution for Combined Data_Synthesizer Pipeline ---
# if __name__ == "__main__":
#     # --- Mapping: Auto-convert Company Name to Ticker ---
#     # Fetch ticker-company mapping using yahoo_fin and yfinance
#     def fetch_ticker_company_mapping(max_tickers=100, delay=1):
#         tickers = si.tickers_nasdaq()
#         mapping = {}
#         count = 0
#         for ticker in tickers:
#             if count >= max_tickers:
#                 break
#             try:
#                 info = yf.Ticker(ticker).info
#                 company = info.get("longName") or info.get("shortName")
#                 if company:
#                     mapping[ticker] = company
#                     count += 1
#             except Exception as e:
#                 continue
#             time.sleep(delay)
#         return mapping

#     mapping = fetch_ticker_company_mapping(max_tickers=100, delay=1)
    
#     user_input = input("Enter stock symbol or company name (e.g., AAPL or Apple): ").strip()
#     # Try to map user input to a ticker
#     input_lower = user_input.lower()
#     symbol = None
#     # First check if the input is already a ticker in the mapping keys
#     if user_input.upper() in mapping:
#         symbol = user_input.upper()
#     else:
#         # Otherwise, search if the input appears in any company name
#         for ticker, company in mapping.items():
#             if input_lower in company.lower():
#                 symbol = ticker
#                 break
#         # If still not found, assume user provided ticker
#         if not symbol:
#             symbol = user_input.upper()
    
#     print(f"Fetching data for ticker: {symbol}")
    
#     # 1. Fetch and combine data from all endpoints
#     documents = preprocess_and_combine(symbol)
#     print("\nTotal documents combined:", len(documents))
    
#     # 2. Build TF-IDF based FAISS index for keyword retrieval
#     index, vectorizer = build_faiss_index(documents)
#     print("FAISS index built with", index.ntotal, "vectors.")
    
#     # 3. Save the combined dataset to disk using Hugging Face Datasets
#     base_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent"
#     dataset_path = f"{base_path}/financial_dataset"
#     dataset = save_dataset(documents, dataset_path)
    
#     # 4. Compute embeddings and add a FAISS index for semantic retrieval (for RAG)
#     dataset = add_embeddings_to_dataset(dataset)
#     index_dir = f"{base_path}/faiss_index"
#     os.makedirs(index_dir, exist_ok=True)
#     index_path = f"{index_dir}/stock_index.index"
#     dataset.get_index("embeddings").save(index_path)
#     print(f"RAG index saved to: {index_path}")
    
#     # 5. Drop the in-memory index and re-save the dataset (for JSON-serializability)
#     dataset.drop_index("embeddings")
#     dataset.save_to_disk(dataset_path)
#     print(f"Dataset with embeddings saved to: {dataset_path}")
    
#     # 6. Load and print sample entries from the final saved dataset (grouped by category)
#     loaded_dataset = load_from_disk(dataset_path)
#     categories = {"Stock Data_Synthesizer": [], "SMA": [], "Fundamental Data_Synthesizer": [], "Yahoo Finance Data_Synthesizer": [], "News Article": []}
#     for entry in loaded_dataset:
#         text = entry["text"]
#         if text.startswith("Stock Data_Synthesizer"):
#             categories["Stock Data_Synthesizer"].append(text)
#         elif text.startswith("SMA"):
#             categories["SMA"].append(text)
#         elif text.startswith("Fundamental Data_Synthesizer"):
#             categories["Fundamental Data_Synthesizer"].append(text)
#         elif text.startswith("Yahoo Finance Data_Synthesizer"):
#             categories["Yahoo Finance Data_Synthesizer"].append(text)
#         elif text.startswith("News Article"):
#             categories["News Article"].append(text)
    
#     print("\n=== Sample entries from the final saved dataset by category ===")
#     for category, texts in categories.items():
#         print(f"\n--- {category} (showing up to 3) ---")
#         for sample in texts[:3]:
#             print(sample)
#             print()


# --- Mapping Integration ---
def load_mapping(filename):
    with open(filename, "r") as f:
        mapping = json.load(f)
    return mapping

def get_ticker_from_input(user_input, mapping, threshold=70):
    # If the input (in uppercase) is directly in the mapping keys, use it.
    if user_input.upper() in mapping:
        return user_input.upper()
    
    # Otherwise, use fuzzy matching to match the input against company names.
    companies = list(mapping.values())
    best_match, score, idx = process.extractOne(user_input, companies, scorer=fuzz.token_sort_ratio)
    if score >= threshold:
        tickers = list(mapping.keys())
        return tickers[idx]
    else:
        # If no good match is found, assume the input is already a ticker.
        return user_input.upper()

if __name__ == "__main__":
    # Load the ticker mapping from the JSON file (produced by tickersymbols.py)
    mapping_file = "ticker_mapping_full.json"
    mapping = load_mapping(mapping_file)
    
    user_input = input("Enter stock symbol or company name (e.g., AAPL or Apple or Crocs): ").strip()
    symbol = get_ticker_from_input(user_input, mapping)
    print(f"Fetching data for ticker: {symbol}")
    
    # 1. Fetch and combine data from all endpoints
    documents = preprocess_and_combine(symbol)
    print("\nTotal documents combined:", len(documents))
    
    # 2. Build TF-IDF based FAISS index for keyword retrieval
    index, vectorizer = build_faiss_index(documents)
    print("FAISS index built with", index.ntotal, "vectors.")
    
    # 3. Save the combined dataset to disk using Hugging Face Datasets
    base_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent"
    dataset_path = f"{base_path}/financial_dataset"
    dataset = save_dataset(documents, dataset_path)
    
    # 4. Compute embeddings and add a FAISS index for semantic retrieval (for RAG)
    dataset = add_embeddings_to_dataset(dataset)
    index_dir = f"{base_path}/faiss_index"
    os.makedirs(index_dir, exist_ok=True)
    index_path = f"{index_dir}/stock_index.index"
    dataset.get_index("embeddings").save(index_path)
    print(f"RAG index saved to: {index_path}")
    
    # 5. Drop the in-memory index and re-save the dataset (for JSON-serializability)
    dataset.drop_index("embeddings")
    dataset.save_to_disk(dataset_path)
    print(f"Dataset with embeddings saved to: {dataset_path}")
    
    # 6. Load and print sample entries from the final saved dataset (grouped by category)
    loaded_dataset = load_from_disk(dataset_path)
    categories = {"Stock Data_Synthesizer": [], "SMA": [], "Fundamental Data_Synthesizer": [], "Yahoo Finance Data_Synthesizer": [], "News Article": []}
    for entry in loaded_dataset:
        text = entry["text"]
        if text.startswith("Stock Data_Synthesizer"):
            categories["Stock Data_Synthesizer"].append(text)
        elif text.startswith("SMA"):
            categories["SMA"].append(text)
        elif text.startswith("Fundamental Data_Synthesizer"):
            categories["Fundamental Data_Synthesizer"].append(text)
        elif text.startswith("Yahoo Finance Data_Synthesizer"):
            categories["Yahoo Finance Data_Synthesizer"].append(text)
        elif text.startswith("News Article"):
            categories["News Article"].append(text)
    
    print("\n=== Sample entries from the final saved dataset by category ===")
    for category, texts in categories.items():
        print(f"\n--- {category} (showing up to 3) ---")
        for sample in texts[:3]:
            print(sample)
            print()

