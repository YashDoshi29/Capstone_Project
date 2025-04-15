# import os
# import time
# import json
# import requests
# import numpy as np
# import faiss
# from datasets import Dataset, load_from_disk
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sentence_transformers import SentenceTransformer
# import yfinance as yf
# from rapidfuzz import process, fuzz
# import torch
# import gc
# from transformers import (
#     RagTokenizer, 
#     RagRetriever,  
#     RagTokenForGeneration, 
#     RagConfig,
#     DPRQuestionEncoderTokenizer,
#     BartTokenizer,
#     DPRContextEncoderTokenizer
# )

# # --- API Keys ---
# ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'
# NEWS_API_KEY = '4c310cb414224d468ee9087dd9f208d6'  # Replace with your actual key

# ### ========================
# ### SECTION 1: Data Pipeline Functions
# ### ========================

# def fetch_stock_data(symbol):
#     url = 'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': ALPHA_VANTAGE_API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching stock data for {symbol}: {response.status_code}")
#         return None

# def preprocess_stock_data(stock_data):
#     if not stock_data:
#         return []
#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found.")
#         return []
#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')
#         document = (
#             f"Stock Data - Date: {date}, Open: {open_price}, High: {high_price}, "
#             f"Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         )
#         documents.append(document)
#     return documents

# def fetch_sma_data(symbol, interval="daily", time_period=50, series_type="close"):
#     url = "https://www.alphavantage.co/query"
#     params = {
#          "function": "SMA",
#          "symbol": symbol,
#          "interval": interval,
#          "time_period": time_period,
#          "series_type": series_type,
#          "apikey": ALPHA_VANTAGE_API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#          return response.json()
#     else:
#          print(f"Error fetching SMA data for {symbol}: {response.status_code}")
#          return None

# def preprocess_sma_data(sma_data):
#     if not sma_data:
#          return []
#     sma_dict = sma_data.get("Technical Analysis: SMA", {})
#     documents = []
#     for date, data in sma_dict.items():
#          sma_value = data.get("SMA", "N/A")
#          document = f"SMA - Date: {date}, SMA: {sma_value}"
#          documents.append(document)
#     return documents

# def fetch_fundamental_data(symbol):
#     url = "https://www.alphavantage.co/query"
#     params = {
#          "function": "OVERVIEW",
#          "symbol": symbol,
#          "apikey": ALPHA_VANTAGE_API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#          return response.json()
#     else:
#          print(f"Error fetching fundamental data for {symbol}: {response.status_code}")
#          return None

# def preprocess_fundamental_data(fund_data):
#     if not fund_data or "Name" not in fund_data:
#          return []
#     company_name = fund_data.get("Name", "N/A")
#     market_cap = fund_data.get("MarketCapitalization", "N/A")
#     pe_ratio = fund_data.get("PERatio", "N/A")
#     document = f"Fundamental Data - Company: {company_name}, MarketCap: {market_cap}, P/E Ratio: {pe_ratio}"
#     return [document]

# # --- Modified News Functions ---
# def fetch_financial_news(query):
#     """
#     Uses the 'everything' endpoint of NewsAPI to fetch all relevant news for a given query.
#     """
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": query,              # search query (e.g., company name)
#         "apiKey": NEWS_API_KEY,
#         "language": "en",
#         "pageSize": 100           # maximum articles per request
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#          return response.json()
#     else:
#          print(f"Error fetching news for query '{query}': {response.status_code}")
#          return None

# def preprocess_news_data(news_data):
#     if not news_data:
#          return []
#     articles = news_data.get('articles', [])
#     documents = []
#     for article in articles:
#          title = article.get('title', '')
#          description = article.get('description', '')
#          content = article.get('content', '')
#          published_at = article.get('publishedAt', '')
#          document = (
#              f"News Article - Date: {published_at}, Title: {title}, "
#              f"Description: {description}, Content: {content}"
#          )
#          documents.append(document)
#     return documents

# def fetch_yahoo_finance_data(symbol):
#     ticker = yf.Ticker(symbol)
#     hist = ticker.history(period="1y", interval="1d")
#     documents = []
#     for date, row in hist.iterrows():
#         doc = f"Yahoo Finance Data - Date: {date.date()}, Open: {row['Open']}, High: {row['High']}, Low: {row['Low']}, Close: {row['Close']}, Volume: {row['Volume']}"
#         documents.append(doc)
#     return documents

# def preprocess_and_combine(symbol, news_query):
#     # Fetch from Alpha Vantage
#     stock_data = fetch_stock_data(symbol)
#     docs_alpha = preprocess_stock_data(stock_data)
    
#     sma_data = fetch_sma_data(symbol)
#     docs_sma = preprocess_sma_data(sma_data)
    
#     fund_data = fetch_fundamental_data(symbol)
#     docs_fund = preprocess_fundamental_data(fund_data)
    
#     docs_yahoo = fetch_yahoo_finance_data(symbol)
    
#     # Fetch Financial News using the provided query
#     news_data = fetch_financial_news(news_query)
#     docs_news = preprocess_news_data(news_data)
    
#     all_documents = docs_alpha + docs_sma + docs_fund + docs_yahoo + docs_news
#     return all_documents

# def build_faiss_index(documents):
#     vectorizer = TfidfVectorizer(stop_words="english")
#     X = vectorizer.fit_transform(documents).toarray()
#     X = np.float32(X)
#     index = faiss.IndexFlatL2(X.shape[1])
#     index.add(X)
#     return index, vectorizer

# def save_dataset(documents, dataset_path):
#     titles = [doc.split(',')[0] for doc in documents]
#     dataset = Dataset.from_dict({
#         "title": titles,
#         "text": documents,
#     })
#     dataset.save_to_disk(dataset_path)
#     print("Dataset saved to:", dataset_path)
#     return dataset

# def add_embeddings_to_dataset(dataset):
#     embedder = SentenceTransformer('all-MiniLM-L6-v2')
#     def compute_embedding(example):
#         full_text = f"{example['title']} {example['text']}"
#         embedding = embedder.encode(full_text).tolist()
#         return {"embeddings": embedding}
#     dataset = dataset.map(compute_embedding)
#     dataset = dataset.add_faiss_index(column="embeddings")
#     return dataset

# ### ============================
# ### SECTION 2: Ticker Mapping Integration
# ### ============================

# def load_mapping(filename):
#     with open(filename, "r") as f:
#         mapping = json.load(f)
#     return mapping

# def get_ticker_from_input(user_input, mapping, threshold=50):
#     if user_input.upper() in mapping:
#         return user_input.upper()
#     companies = list(mapping.values())
#     best_match, score, idx = process.extractOne(user_input, companies, scorer=fuzz.token_sort_ratio)
#     if score >= threshold:
#         tickers = list(mapping.keys())
#         return tickers[idx]
#     else:
#         return user_input.upper()

# ### ============================
# ### SECTION 3: RAG Model and Query Extraction
# ### ============================

# def setup_rag_model(index_dir, dataset_path):
#     try:
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#         gc.collect()
        
#         custom_dataset = load_from_disk(dataset_path)
        
#         config = RagConfig.from_pretrained("facebook/rag-token-nq")
#         config.forced_bos_token_id = 0
#         config.index_name = "custom"
#         config.passages_path = dataset_path
#         config.index_path = f"{index_dir}/stock_index.index"
        
#         question_encoder_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
#             "facebook/dpr-question_encoder-single-nq-base"
#         )
#         context_encoder_tokenizer = DPRContextEncoderTokenizer.from_pretrained(
#             "facebook/dpr-ctx_encoder-single-nq-base"
#         )
#         generator_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")
        
#         rag_tokenizer = RagTokenizer(
#             question_encoder=question_encoder_tokenizer,
#             generator=generator_tokenizer
#         )
        
#         retriever = RagRetriever.from_pretrained(
#             "facebook/rag-token-nq",
#             config=config,
#             question_encoder_tokenizer=question_encoder_tokenizer,
#             generator_tokenizer=generator_tokenizer,
#             index_name="custom"
#         )
#         retriever.passages = custom_dataset
        
#         model = RagTokenForGeneration.from_pretrained(
#             "facebook/rag-token-nq",
#             config=config,
#             retriever=retriever,
#             use_cache=False
#         )
        
#         return retriever, rag_tokenizer, model
#     except Exception as e:
#         print(f"Error in setup_rag_model: {str(e)}")
#         raise

# def custom_retrieve(query, faiss_index, documents, vectorizer, top_k=3):
#     query_vector = vectorizer.transform([query]).toarray().astype(np.float32)
#     distances, indices = faiss_index.search(query_vector, top_k)
#     retrieved_docs = [documents[i] for i in indices[0]]
#     return retrieved_docs

# def answer_query(query, retrieved_docs, rag_model, rag_tokenizer):
#     context = query + "\n" + "\n".join(retrieved_docs)
#     inputs = rag_tokenizer(context, return_tensors="pt")
#     outputs = rag_model.generate(input_ids=inputs["input_ids"])
#     answer = rag_tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return answer

# ### ============================
# ### SECTION 4: Main Execution
# ### ============================

# if __name__ == "__main__":
#     # 1. Load the ticker mapping from the JSON file
#     mapping_file = "ticker_mapping_full.json"
#     mapping = load_mapping(mapping_file)
    
#     # 2. Get user input and convert to correct ticker using fuzzy matching
#     user_input = input("Enter stock symbol or company name (e.g., AAPL or Apple): ").strip()
#     symbol = get_ticker_from_input(user_input, mapping)
#     print(f"Fetching data for ticker: {symbol}")
    
#     # Determine the news query: if symbol is in mapping, use the mapped company name; otherwise, use user input.
#     news_query = mapping.get(symbol, user_input)
    
#     # 3. Build the dataset for that ticker (including news specific to the company)
#     documents = preprocess_and_combine(symbol, news_query)
#     print("\nTotal documents combined:", len(documents))
    
#     # 4. Build a TF-IDF based FAISS index for keyword retrieval
#     index, vectorizer = build_faiss_index(documents)
#     print("FAISS index built with", index.ntotal, "vectors.")
    
#     # 5. Save the dataset using Hugging Face Datasets
#     base_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent"
#     dataset_path = f"{base_path}/financial_dataset"
#     dataset = save_dataset(documents, dataset_path)
    
#     # 6. Compute embeddings and add a FAISS index for semantic retrieval (for RAG)
#     dataset = add_embeddings_to_dataset(dataset)
#     index_dir = f"{base_path}/faiss_index"
#     os.makedirs(index_dir, exist_ok=True)
#     index_path = f"{index_dir}/stock_index.index"
#     dataset.get_index("embeddings").save(index_path)
#     print(f"RAG index saved to: {index_path}")
    
#     # 7. Drop the in-memory index and re-save the dataset
#     dataset.drop_index("embeddings")
#     dataset.save_to_disk(dataset_path)
#     print(f"Dataset with embeddings saved to: {dataset_path}")
    
#     # 8. Load and display sample entries from the final saved dataset by category
#     loaded_dataset = load_from_disk(dataset_path)
#     categories = {"Stock Data": [], "SMA": [], "Fundamental Data": [], "Yahoo Finance Data": [], "News Article": []}
#     for entry in loaded_dataset:
#         text = entry["text"]
#         if text.startswith("Stock Data"):
#             categories["Stock Data"].append(text)
#         elif text.startswith("SMA"):
#             categories["SMA"].append(text)
#         elif text.startswith("Fundamental Data"):
#             categories["Fundamental Data"].append(text)
#         elif text.startswith("Yahoo Finance Data"):
#             categories["Yahoo Finance Data"].append(text)
#         elif text.startswith("News Article"):
#             categories["News Article"].append(text)
    
#     print("\n=== Sample entries from the final saved dataset by category ===")
#     for category, texts in categories.items():
#         print(f"\n--- {category} (showing up to 5) ---")
#         for sample in texts[:5]:
#             print(sample)
#             print()
    
#     # 9. Set up the RAG model using the saved dataset and index
#     retriever, rag_tokenizer, rag_model = setup_rag_model(index_dir, dataset_path)
    
#     # 10. Get a query from the user and use the RAG model to answer it
#     query = input("Enter your financial query: ").strip()
#     retrieved_docs = custom_retrieve(query, index, documents, vectorizer)
#     final_answer = answer_query(query, retrieved_docs, rag_model, rag_tokenizer)
    
#     print("\nFinal Answer:")
#     print(final_answer)


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
from rapidfuzz import process, fuzz
import torch
import gc
from transformers import (
    RagTokenizer, 
    RagRetriever,  
    RagTokenForGeneration, 
    RagConfig,
    DPRQuestionEncoderTokenizer,
    BartTokenizer,
    DPRContextEncoderTokenizer
)

# --- API Keys ---
ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'
NEWS_API_KEY = '4c310cb414224d468ee9087dd9f208d6'  # Replace with your actual key

### ========================
### SECTION 1: Data Pipeline Functions
### ========================

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
            f"Stock Data - Date: {date}, Open: {open_price}, High: {high_price}, "
            f"Low: {low_price}, Close: {close_price}, Volume: {volume}"
        )
        documents.append(document)
    return documents

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
    company_name = fund_data.get("Name", "N/A")
    market_cap = fund_data.get("MarketCapitalization", "N/A")
    pe_ratio = fund_data.get("PERatio", "N/A")
    document = f"Fundamental Data - Company: {company_name}, MarketCap: {market_cap}, P/E Ratio: {pe_ratio}"
    return [document]

# --- Modified News Functions ---
def fetch_financial_news(query):
    """
    Uses the 'everything' endpoint of NewsAPI to fetch all relevant news for a given query.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,              # search query (e.g., company name)
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 100           # maximum articles per request
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
         return response.json()
    else:
         print(f"Error fetching news for query '{query}': {response.status_code}")
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

def fetch_yahoo_finance_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y", interval="1d")
    documents = []
    for date, row in hist.iterrows():
        doc = f"Yahoo Finance Data - Date: {date.date()}, Open: {row['Open']}, High: {row['High']}, Low: {row['Low']}, Close: {row['Close']}, Volume: {row['Volume']}"
        documents.append(doc)
    return documents

def preprocess_and_combine(symbol, news_query):
    # Fetch from Alpha Vantage
    stock_data = fetch_stock_data(symbol)
    docs_alpha = preprocess_stock_data(stock_data)
    
    sma_data = fetch_sma_data(symbol)
    docs_sma = preprocess_sma_data(sma_data)
    
    fund_data = fetch_fundamental_data(symbol)
    docs_fund = preprocess_fundamental_data(fund_data)
    
    docs_yahoo = fetch_yahoo_finance_data(symbol)
    
    # Fetch Financial News using the provided query
    news_data = fetch_financial_news(news_query)
    docs_news = preprocess_news_data(news_data)
    
    all_documents = docs_alpha + docs_sma + docs_fund + docs_yahoo + docs_news
    return all_documents

def build_faiss_index(documents):
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(documents).toarray()
    X = np.float32(X)
    index = faiss.IndexFlatL2(X.shape[1])
    index.add(X)
    return index, vectorizer

def save_dataset(documents, dataset_path):
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

### ============================
### SECTION 2: Ticker Mapping Integration
### ============================

def load_mapping(filename):
    with open(filename, "r") as f:
        mapping = json.load(f)
    return mapping

def get_ticker_from_input(user_input, mapping, threshold=50):
    if user_input.upper() in mapping:
        return user_input.upper()
    companies = list(mapping.values())
    best_match, score, idx = process.extractOne(user_input, companies, scorer=fuzz.token_sort_ratio)
    if score >= threshold:
        tickers = list(mapping.keys())
        return tickers[idx]
    else:
        return user_input.upper()

### ============================
### SECTION 3: RAG Model and Query Extraction
### ============================

def setup_rag_model(index_dir, dataset_path):
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        custom_dataset = load_from_disk(dataset_path)
        
        config = RagConfig.from_pretrained("facebook/rag-token-nq")
        config.forced_bos_token_id = 0
        config.index_name = "custom"
        config.passages_path = dataset_path
        config.index_path = f"{index_dir}/stock_index.index"
        
        question_encoder_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
            "facebook/dpr-question_encoder-single-nq-base"
        )
        context_encoder_tokenizer = DPRContextEncoderTokenizer.from_pretrained(
            "facebook/dpr-ctx_encoder-single-nq-base"
        )
        generator_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")
        
        rag_tokenizer = RagTokenizer(
            question_encoder=question_encoder_tokenizer,
            generator=generator_tokenizer
        )
        
        retriever = RagRetriever.from_pretrained(
            "facebook/rag-token-nq",
            config=config,
            question_encoder_tokenizer=question_encoder_tokenizer,
            generator_tokenizer=generator_tokenizer,
            index_name="custom"
        )
        retriever.passages = custom_dataset
        
        model = RagTokenForGeneration.from_pretrained(
            "facebook/rag-token-nq",
            config=config,
            retriever=retriever,
            use_cache=False
        )
        
        return retriever, rag_tokenizer, model
    except Exception as e:
        print(f"Error in setup_rag_model: {str(e)}")
        raise

def custom_retrieve(query, faiss_index, documents, vectorizer, top_k=3):
    query_vector = vectorizer.transform([query]).toarray().astype(np.float32)
    distances, indices = faiss_index.search(query_vector, top_k)
    retrieved_docs = [documents[i] for i in indices[0]]
    return retrieved_docs

def answer_query(query, retrieved_docs, rag_model, rag_tokenizer):
    context = query + "\n" + "\n".join(retrieved_docs)
    inputs = rag_tokenizer(context, return_tensors="pt")
    outputs = rag_model.generate(input_ids=inputs["input_ids"])
    answer = rag_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

### ============================
### SECTION 4: Main Execution
### ============================

if __name__ == "__main__":
    # 1. Load the ticker mapping from the JSON file
    mapping_file = "ticker_mapping_full.json"
    mapping = load_mapping(mapping_file)
    
    # 2. Get user input and convert to correct ticker using fuzzy matching
    user_input = input("Enter stock symbol or company name (e.g., AAPL or Apple): ").strip()
    symbol = get_ticker_from_input(user_input, mapping)
    print(f"Fetching data for ticker: {symbol}")
    
    # Determine the news query: if symbol is in mapping, use the mapped company name; otherwise, use user input.
    news_query = mapping.get(symbol, user_input)
    
    # 3. Build the dataset for that ticker (including news specific to the company)
    documents = preprocess_and_combine(symbol, news_query)
    print("\nTotal documents combined:", len(documents))
    
    # 4. Build a TF-IDF based FAISS index for keyword retrieval
    index, vectorizer = build_faiss_index(documents)
    print("FAISS index built with", index.ntotal, "vectors.")
    
    # 5. Save the dataset using Hugging Face Datasets
    base_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent"
    dataset_path = f"{base_path}/financial_dataset"
    dataset = save_dataset(documents, dataset_path)
    
    # 6. Compute embeddings and add a FAISS index for semantic retrieval (for RAG)
    dataset = add_embeddings_to_dataset(dataset)
    index_dir = f"{base_path}/faiss_index"
    os.makedirs(index_dir, exist_ok=True)
    index_path = f"{index_dir}/stock_index.index"
    dataset.get_index("embeddings").save(index_path)
    print(f"RAG index saved to: {index_path}")
    
    # 7. Drop the in-memory index and re-save the dataset
    dataset.drop_index("embeddings")
    dataset.save_to_disk(dataset_path)
    print(f"Dataset with embeddings saved to: {dataset_path}")
    
    # 8. Load and display sample entries from the final saved dataset by category
    loaded_dataset = load_from_disk(dataset_path)
    categories = {"Stock Data": [], "SMA": [], "Fundamental Data": [], "Yahoo Finance Data": [], "News Article": []}
    for entry in loaded_dataset:
        text = entry["text"]
        if text.startswith("Stock Data"):
            categories["Stock Data"].append(text)
        elif text.startswith("SMA"):
            categories["SMA"].append(text)
        elif text.startswith("Fundamental Data"):
            categories["Fundamental Data"].append(text)
        elif text.startswith("Yahoo Finance Data"):
            categories["Yahoo Finance Data"].append(text)
        elif text.startswith("News Article"):
            categories["News Article"].append(text)
    
    print("\n=== Sample entries from the final saved dataset by category ===")
    for category, texts in categories.items():
        print(f"\n--- {category} (showing up to 5) ---")
        for sample in texts[:5]:
            print(sample)
            print()
    
    # 9. Set up the RAG model using the saved dataset and index
    retriever, rag_tokenizer, rag_model = setup_rag_model(index_dir, dataset_path)
    
    # 10. Get a query from the user and use the RAG model to answer it
    query = input("Enter your financial query: ").strip()
    retrieved_docs = custom_retrieve(query, index, documents, vectorizer)
    final_answer = answer_query(query, retrieved_docs, rag_model, rag_tokenizer)
    
    print("\nFinal Answer:")
    print(final_answer)


