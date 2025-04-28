
# import os
# import requests
# from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import nltk
# import logging
# from dotenv import load_dotenv
# import yfinance as yf

# # Initialize
# load_dotenv()
# nltk.download('vader_lexicon')
# app = Flask(__name__)
# CORS(app)
# logging.basicConfig(level=logging.INFO)

# # Configuration
# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvidia': 'NVDA',
#     'amd': 'AMD',
#     'johnson & johnson': 'JNJ',
#     'jnj': 'JNJ',
#     'pfizer': 'PFE',
#     'pfe': 'PFE',
#     'jpmorgan': 'JPM',
#     'jpm': 'JPM',
#     'goldman sachs': 'GS',
#     'gs': 'GS',
#     'coca cola': 'KO',
#     'ko': 'KO',
#     'pepsi': 'PEP',
#     'pep': 'PEP',
#     'exxon': 'XOM',
#     'xom': 'XOM',
#     'next era energy': 'NEE',
#     'nee': 'NEE',
#     'chevron': 'CVX',
#     'cvx': 'CVX',
#     'walmart': 'WMT',
#     'wmt': 'WMT',
#     'home depot': 'HD',
#     'hd': 'HD',
#     'gamestop': 'GME',
#     'gme': 'GME',
#     'tesla': 'TSLA',
#     'tsla': 'TSLA',
#     'ford': 'F',
#     'f': 'F',
#     'coinbase': 'COIN',
#     'coin': 'COIN',
#     'moderna': 'MRNA',
#     'mrna': 'MRNA'
# }

# # Load models
# finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
# roberta = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()
# gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")

# # def fetch_news(ticker):
# #     """Fetch news using NewsAPI with proper error handling"""
# #     NEWS_API_KEY =   # Your actual key
    
# #     if not NEWS_API_KEY:
# #         raise ValueError("NewsAPI key not configured")
    
# #     company_name = next((k for k, v in COMPANY_NAME_TO_TICKER.items() if v == ticker), ticker)
# #     url = f"https://newsapi.org/v2/everything?q={company_name}+stock&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    
# #     try:
# #         response = requests.get(url, timeout=10)
# #         data = response.json()
        
# #         if data['status'] != 'ok':
# #             raise ValueError(data.get('message', 'NewsAPI error'))
        
# #         return [
# #             (article['title'], article['source']['name'])
# #             for article in data['articles']
# #         ]
# #     except Exception as e:
# #         logging.error(f"News fetch failed: {str(e)}")
# #         raise ValueError(f"Could not fetch news: {str(e)}")

# def fetch_news(ticker):
#     """Fetch stock-related news with ticker symbol directly for better relevance."""
#     NEWS_API_KEY = ""  # Your actual key
    
#     if not NEWS_API_KEY:
#         raise ValueError("NewsAPI key not configured")
    
#     # Directly use the stock ticker symbol in the query and broaden the search
#     query = f"{ticker} stock news"  # Simplified query
#     url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
#     try:
#         response = requests.get(url, timeout=10)
#         data = response.json()

#         # Check if the response is successful
#         if data['status'] != 'ok':
#             raise ValueError(data.get('message', 'NewsAPI error'))

#         # If no articles, log it
#         if not data['articles']:
#             logging.warning(f"No articles found for ticker {ticker}.")
        
#         # Return the fetched articles (with more relevant stock-related titles)
#         return [
#             (article['title'], article['source']['name'], article['description'], article['url'])
#             for article in data['articles']
#             if 'stock' in article['title'].lower() or 'earnings' in article['title'].lower()
#         ]
    
#     except Exception as e:
#         logging.error(f"News fetch failed: {str(e)}")
#         raise ValueError(f"Could not fetch news: {str(e)}")

# # EVERYTHING BELOW THIS LINE REMAINS EXACTLY THE SAME >>>>>>>>>>>>>>>>>>>>>>>>>>
# def get_stock_data(ticker):
#     """Get current stock price using yfinance"""
#     stock = yf.Ticker(ticker)
#     data = stock.history(period='1d')
#     if data.empty:
#         return None
#     return {
#         'current_price': round(data['Close'].iloc[-1], 2),
#         'change': round(data['Close'].iloc[-1] - data['Open'].iloc[-1], 2),
#         'change_percent': round(((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100, 2)
#     }

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis"""
#     # Get predictions
#     finbert_result = finbert(text)[0]
#     roberta_result = roberta(text)[0]
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Convert to common scale (-1 to 1)
#     finbert_score = 1 if finbert_result['label'] == 'Positive' else -1 if finbert_result['label'] == 'Negative' else 0
#     roberta_score = (roberta_result['score'] if roberta_result['label'] == 'POS' else 
#                     -roberta_result['score'] if roberta_result['label'] == 'NEG' else 0)
    
#     # Fixed weights (calibrated for stability)
#     weighted_score = (0.6 * finbert_score) + (0.3 * roberta_score) + (0.1 * vader_score)
    
#     # Classify with hysteresis to reduce fluctuation
#     if weighted_score > 0.35: return 'Positive', weighted_score
#     if weighted_score < -0.35: return 'Negative', weighted_score
#     return 'Neutral', weighted_score

# def generate_analysis(ticker, news_items, overall_sentiment):
#     """Generate GPT-2 powered analysis"""
#     prompt = f"Analyze {ticker} stock sentiment based on these news headlines:\n"
#     prompt += "\n".join([f"- {headline}" for headline, _ in news_items])
#     prompt += f"\n\nOverall sentiment is {overall_sentiment}. Provide concise investment advice:"
    
#     inputs = gpt2_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
#     outputs = gpt2_model.generate(
#         **inputs,
#         max_length=200,
#         num_return_sequences=1,
#         temperature=0.7,
#         do_sample=True
#     )
    
#     return gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     """List supported tickers"""
#     return jsonify({
#         "tickers": SUPPORTED_TICKERS,
#         "mappings": COMPANY_NAME_TO_TICKER
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     """Main analysis endpoint"""
#     ticker_or_name = request.args.get('stock', '').upper()
    
#     # Resolve input to ticker
#     ticker = None
#     if ticker_or_name in SUPPORTED_TICKERS:
#         ticker = ticker_or_name
#     elif ticker_or_name.lower() in COMPANY_NAME_TO_TICKER:
#         ticker = COMPANY_NAME_TO_TICKER[ticker_or_name.lower()]
    
#     if not ticker:
#         return jsonify({"error": "Unsupported stock"}), 400
    
#     try:
#         # Fetch all data
#         news_items = fetch_news(ticker)
#         stock_data = get_stock_data(ticker)
        
#         # Analyze sentiment
#         analyzed_news = []
#         sentiment_scores = []
        
#         for headline, source in news_items:
#             sentiment, score = analyze_sentiment(headline)
#             analyzed_news.append({
#                 "headline": headline,
#                 "source": source,
#                 "sentiment": sentiment,
#                 "score": round(score, 2)
#             })
#             sentiment_scores.append(score)
        
#         # Calculate overall
#         avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
#         overall_sentiment = "Positive" if avg_score > 0.35 else "Negative" if avg_score < -0.35 else "Neutral"
        
#         # Generate GPT-2 analysis
#         gpt_analysis = generate_analysis(ticker, news_items, overall_sentiment)
        
#         return jsonify({
#             "ticker": ticker,
#             "news": analyzed_news,
#             "stock_data": stock_data,
#             "overall_sentiment": overall_sentiment,
#             "average_score": round(avg_score, 2),
#             "analysis": gpt_analysis
#         })
        
#     except Exception as e:
#         logging.error(f"Analysis failed: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001)


# import os
# import requests
# from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import nltk
# import logging
# from dotenv import load_dotenv
# import yfinance as yf

# # Initialize
# load_dotenv()
# nltk.download('vader_lexicon')
# app = Flask(__name__)
# CORS(app)
# logging.basicConfig(level=logging.INFO)

# # Configuration
# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvidia': 'NVDA',
#     'amd': 'AMD',
#     'johnson & johnson': 'JNJ',
#     'jnj': 'JNJ',
#     'pfizer': 'PFE',
#     'pfe': 'PFE',
#     'jpmorgan': 'JPM',
#     'jpm': 'JPM',
#     'goldman sachs': 'GS',
#     'gs': 'GS',
#     'coca cola': 'KO',
#     'ko': 'KO',
#     'pepsi': 'PEP',
#     'pep': 'PEP',
#     'exxon': 'XOM',
#     'xom': 'XOM',
#     'next era energy': 'NEE',
#     'nee': 'NEE',
#     'chevron': 'CVX',
#     'cvx': 'CVX',
#     'walmart': 'WMT',
#     'wmt': 'WMT',
#     'home depot': 'HD',
#     'hd': 'HD',
#     'gamestop': 'GME',
#     'gme': 'GME',
#     'tesla': 'TSLA',
#     'tsla': 'TSLA',
#     'ford': 'F',
#     'f': 'F',
#     'coinbase': 'COIN',
#     'coin': 'COIN',
#     'moderna': 'MRNA',
#     'mrna': 'MRNA'
# }

# # Load models
# finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
# roberta = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()
# gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")

# # Fetch stock-related news with ticker symbol directly for better relevance
# def fetch_news(ticker):
#     """Fetch stock-related news with ticker symbol directly for better relevance."""
#     NEWS_API_KEY = ""  # Your actual key
    
#     if not NEWS_API_KEY:
#         raise ValueError("NewsAPI key not configured")
    
#     # Directly use the stock ticker symbol in the query and broaden the search
#     query = f"{ticker} stock news"  # Simplified query
#     url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
#     try:
#         response = requests.get(url, timeout=10)
#         data = response.json()

#         # Check if the response is successful
#         if data['status'] != 'ok':
#             raise ValueError(data.get('message', 'NewsAPI error'))

#         # If no articles, log it
#         if not data['articles']:
#             logging.warning(f"No articles found for ticker {ticker}.")
        
#         # Return the fetched articles (with more relevant stock-related titles)
#         return [
#             (article['title'], article['source']['name'], article['description'], article['url'])
#             for article in data['articles']
#             if 'stock' in article['title'].lower() or 'earnings' in article['title'].lower()
#         ]
    
#     except Exception as e:
#         logging.error(f"News fetch failed: {str(e)}")
#         raise ValueError(f"Could not fetch news: {str(e)}")

# # Get stock data using yfinance
# def get_stock_data(ticker):
#     """Get current stock price using yfinance"""
#     stock = yf.Ticker(ticker)
#     data = stock.history(period='1d')
#     if data.empty:
#         return None
#     return {
#         'current_price': round(data['Close'].iloc[-1], 2),
#         'change': round(data['Close'].iloc[-1] - data['Open'].iloc[-1], 2),
#         'change_percent': round(((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100, 2)
#     }

# # Sentiment analysis using multiple models
# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis"""
#     # Get predictions
#     finbert_result = finbert(text)[0]
#     roberta_result = roberta(text)[0]
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Convert to common scale (-1 to 1)
#     finbert_score = 1 if finbert_result['label'] == 'Positive' else -1 if finbert_result['label'] == 'Negative' else 0
#     roberta_score = (roberta_result['score'] if roberta_result['label'] == 'POS' else 
#                     -roberta_result['score'] if roberta_result['label'] == 'NEG' else 0)
    
#     # Fixed weights (calibrated for stability)
#     weighted_score = (0.6 * finbert_score) + (0.3 * roberta_score) + (0.1 * vader_score)
    
#     # Classify with hysteresis to reduce fluctuation
#     if weighted_score > 0.35: return 'Positive', weighted_score
#     if weighted_score < -0.35: return 'Negative', weighted_score
#     return 'Neutral', weighted_score

# # GPT-2 model powered analysis generation
# def generate_analysis(ticker, news_items, overall_sentiment):
#     """Generate GPT-2 powered analysis"""
#     prompt = f"Analyze {ticker} stock sentiment based on these news headlines:\n"
#     prompt += "\n".join([f"- {headline}" for headline, _ in news_items])
#     prompt += f"\n\nOverall sentiment is {overall_sentiment}. Provide concise investment advice:"
    
#     inputs = gpt2_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
#     outputs = gpt2_model.generate(
#         **inputs,
#         max_length=200,
#         num_return_sequences=1,
#         temperature=0.7,
#         do_sample=True
#     )
    
#     return gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

# # Endpoint to fetch supported tickers
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     """List supported tickers"""
#     return jsonify({
#         "tickers": SUPPORTED_TICKERS,
#         "mappings": COMPANY_NAME_TO_TICKER
#     })

# # Main analysis endpoint
# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     """Main analysis endpoint"""
#     ticker_or_name = request.args.get('stock', '').upper()
    
#     # Resolve input to ticker
#     ticker = None
#     if ticker_or_name in SUPPORTED_TICKERS:
#         ticker = ticker_or_name
#     elif ticker_or_name.lower() in COMPANY_NAME_TO_TICKER:
#         ticker = COMPANY_NAME_TO_TICKER[ticker_or_name.lower()]
    
#     if not ticker:
#         return jsonify({"error": "Unsupported stock"}), 400
    
#     try:
#         # Fetch all data
#         news_items = fetch_news(ticker)
#         stock_data = get_stock_data(ticker)
        
#         # Analyze sentiment
#         analyzed_news = []
#         sentiment_scores = []
        
#         for headline, source, description, url in news_items:
#             sentiment, score = analyze_sentiment(headline)  # Correct unpacking here
#             analyzed_news.append({
#                 "headline": headline,
#                 "source": source,
#                 "sentiment": sentiment,
#                 "score": round(score, 2),
#                 "description": description,
#                 "url": url  # Add URL to the response
#             })
#             sentiment_scores.append(score)
        
#         # Calculate overall
#         avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
#         overall_sentiment = "Positive" if avg_score > 0.35 else "Negative" if avg_score < -0.35 else "Neutral"
        
#         # Generate GPT-2 analysis
#         gpt_analysis = generate_analysis(ticker, news_items, overall_sentiment)
        
#         return jsonify({
#             "ticker": ticker,
#             "news": analyzed_news,
#             "stock_data": stock_data,
#             "overall_sentiment": overall_sentiment,
#             "average_score": round(avg_score, 2),
#             "analysis": gpt_analysis
#         })
        
#     except Exception as e:
#         logging.error(f"Analysis failed: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001)




# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')

# # ─────────────────────────────────────────────────────────────────────────────
# # New imports for ensemble sentiment (from Code B)
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ─────────────────────────────────────────────────────────────────────────────

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = ""  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol."""
#     try:
#         company = yf.Ticker(ticker)
        
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Clean and format the data
#         if balance_sheet.shape[1] >= 3:
#             balance_sheet = balance_sheet.iloc[:, :3]  # Keep first 3 years
#         balance_sheet = balance_sheet.dropna(how="any")  # Drop rows with NaN values

#         # Convert the data to strings for easy display
#         balance_sheet_str = balance_sheet.to_string()
#         income_statement_str = income_statement.to_string()
#         cashflow_statement_str = cashflow_statement.to_string()

#         return {
#             "balance_sheet": balance_sheet_str,
#             "income_statement": income_statement_str,
#             "cashflow_statement": cashflow_statement_str
#         }
#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {
#             "balance_sheet": "Error fetching balance sheet.",
#             "income_statement": "Error fetching income statement.",
#             "cashflow_statement": "Error fetching cash flow statement."
#         }

# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # FinBERT-based Sentiment Analysis (original)
# # ---------------------------
# from transformers import pipeline
# finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# def analyze_news_sentiment(news_list):
#     sentiments = []
#     for headline in news_list:
#         try:
#             result = finbert(headline)[0]
#             sentiments.append(result)
#         except Exception:
#             sentiments.append({"label": "Neutral", "score": 0.0})
#     return sentiments

# def aggregate_sentiments(sentiments):
#     if not sentiments:
#         return "Neutral"
#     positive = sum(s['score'] for s in sentiments if s['label'].lower() == 'positive')
#     negative = sum(s['score'] for s in sentiments if s['label'].lower() == 'negative')
#     neutral = sum(s['score'] for s in sentiments if s['label'].lower() == 'neutral')
#     total = positive + negative + neutral
#     pos_pct = positive / total if total > 0 else 0
#     neg_pct = negative / total if total > 0 else 0
#     if pos_pct > neg_pct:
#         return "Positive"
#     elif neg_pct > pos_pct:
#         return "Negative"
#     else:
#         return "Neutral"

# # ─────────────────────────────────────────────────────────────────────────────
# # Ensemble sentiment function copied **verbatim** from Code B:
# # ─────────────────────────────────────────────────────────────────────────────
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis from Code B."""
#     finbert_result  = finbert(text)[0]
#     roberta_result  = roberta(text)[0]
#     vader_score     = vader.polarity_scores(text)['compound']

#     # map labels to -1/0/+1
#     finbert_score  =  1 if finbert_result['label'] == 'Positive' \
#                     else -1 if finbert_result['label'] == 'Negative' \
#                     else 0
#     roberta_score  =  roberta_result['score'] if roberta_result['label'] == 'POS' \
#                     else -roberta_result['score'] if roberta_result['label'] == 'NEG' \
#                     else 0

#     weighted_score = (0.6 * finbert_score) + (0.3 * roberta_score) + (0.1 * vader_score)

#     if weighted_score > 0.35:
#         label = 'Positive'
#     elif weighted_score < -0.35:
#         label = 'Negative'
#     else:
#         label = 'Neutral'

#     return label, weighted_score
# # ─────────────────────────────────────────────────────────────────────────────

# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# # ---------------------------
# # API Endpoints
# # ---------------------------

# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; ...'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}". ...'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         stock = yf.Ticker(ticker)
#         hist  = stock.history(period="1mo")
#         info  = stock.info

#         current_price   = hist['Close'].iloc[-1]
#         open_price      = hist['Open'].iloc[-1]
#         high_price      = hist['High'].iloc[-1]
#         low_price       = hist['Low'].iloc[-1]
#         previous_close  = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume          = hist['Volume'].iloc[-1]

#         sma_10          = hist['Close'].rolling(10).mean().iloc[-1]
#         trend           = "up" if current_price > sma_10 else "down"
#         price_change    = (current_price - previous_close) / previous_close
#         volatility      = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)

#         # original FinBERT-only sentiments
#         sentiments = analyze_news_sentiment(news_list)
#         overall_sentiment = aggregate_sentiments(sentiments)

#         # ─────────────── New: ensemble sentiment scores ───────────────
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })
#         # ────────────────────────────────────────────────────────────────

#         # Fetch financial statement sentiment
#         financial_sentiment_data = get_financial_statements(ticker)
#         financial_sentiment = "Neutral"  # Example placeholder for sentiment
#         financial_statements_content = financial_sentiment_data.get("balance_sheet", "No content available")

#         # Rule-based decision
#         if trend == "up" and overall_sentiment == "Positive":
#             decision = "Buy"
#         elif trend == "down" and overall_sentiment == "Negative":
#             decision = "Sell"
#         else:
#             decision = "Hold"

#         analysis = (
#             f"Based on technical analysis, {ticker} is trading at ${current_price:.2f} ..."
#         )

#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_sentiment,
#             'financial_statements_content': financial_statements_content,
#             'analysis': analysis
#         }
#         return jsonify(response)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/recommend', methods=['GET'])
# def recommend_stocks():
#     try:
#         amount = float(request.args.get('amount', user_profile['available_amount']))
#         risk = request.args.get('risk', user_profile['risk_preference'])
#         if risk not in RISK_LEVELS:
#             return jsonify({'error': 'Invalid risk level'}), 400

#         candidates = []
#         for ticker in RISK_LEVELS[risk]:
#             try:
#                 stock = yf.Ticker(ticker)
#                 hist = stock.history(period="1mo")
#                 current_price = hist['Close'].iloc[-1]
#                 previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
#                 sma_10 = hist['Close'].rolling(10).mean().iloc[-1]
#                 price_change = (current_price - previous_close) / previous_close
#                 price_change_3d = (current_price - hist['Close'].iloc[-4]) / hist['Close'].iloc[-4] if len(hist) >= 4 else 0
#                 is_uptrend = current_price > sma_10
#                 is_recovering = price_change_3d > 0

#                 confidence = 0.5
#                 if is_uptrend:
#                     confidence += 0.3
#                 elif not is_recovering:
#                     confidence -= 0.1
#                 else:
#                     confidence += 0.1
#                 confidence += min(0.2, price_change_3d * 3)
#                 confidence = max(0.2, min(0.9, confidence))
                
#                 candidates.append({
#                     'ticker': ticker,
#                     'price': round(current_price, 2),
#                     'confidence': confidence,
#                     'trend': 'up' if is_uptrend else ('recovering' if is_recovering else 'down'),
#                     'sector': SECTOR_MAP.get(ticker, 'other')
#                 })
#             except Exception as e:
#                 app.logger.error(f"Error processing {ticker}: {str(e)}")
#                 continue

#         candidates.sort(key=lambda x: x['confidence'], reverse=True)
#         top_picks = candidates[:3]
#         if not top_picks:
#             return jsonify({
#                 'status': 'success',
#                 'recommendations': [],
#                 'allocation_plan': []
#             })

#         total_confidence = sum(x['confidence'] for x in top_picks)
#         allocation = []
#         for stock in top_picks:
#             weight = stock['confidence'] / total_confidence
#             allocated = round(amount * weight, 2)
#             shares = max(1, int(allocated / stock['price']))
#             allocation.append({
#                 'ticker': stock['ticker'],
#                 'amount': allocated,
#                 'shares': shares,
#                 'percentage': round(weight * 100, 1)
#             })
#             stock['shares'] = shares

#         return jsonify({
#             'status': 'success',
#             'recommendations': top_picks,
#             'allocation_plan': allocation
#         })
#     except Exception as e:
#         return jsonify({
#             'error': str(e),
#             'message': 'Failed to generate recommendations'
#         }), 500

# @app.route('/api/update_profile', methods=['POST'])
# def update_profile():
#     try:
#         data = request.get_json()
#         user_profile['available_amount'] = float(data.get('amount', 5000.0))
#         user_profile['risk_preference'] = data.get('risk', 'medium')
#         return jsonify({'status': 'profile_updated'})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)





# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')

# # ─────────────────────────────────────────────────────────────────────────────
# # Correct import for the transformer pipeline
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ─────────────────────────────────────────────────────────────────────────────

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = ""  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Sentiment Analysis (FinBERT, RoBERTa, VADER)
# # ---------------------------
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Corrected pipeline import
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
    
#     # Sentiment from FinBERT
#     finbert_result = finbert(text)[0]
#     finbert_label = finbert_result['label']
#     finbert_score = finbert_result['score']
    
#     # Sentiment from RoBERTa
#     roberta_result = roberta(text)[0]
#     roberta_label = roberta_result['label']
#     roberta_score = roberta_result['score']
    
#     # Sentiment from VADER
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Map FinBERT result to score: Positive (1), Neutral (0), Negative (-1)
#     finbert_score = 1 if finbert_label == 'Positive' else -1 if finbert_label == 'Negative' else 0
    
#     # Map RoBERTa result to score: Positive (1), Neutral (0), Negative (-1)
#     roberta_score = roberta_score if roberta_label == 'POS' else -roberta_score if roberta_label == 'NEG' else 0
    
#     # VADER score is already a numeric value between -1 and 1 (no need for mapping)
#     vader_weighted_score = vader_score  # VADER score can directly be used for weighting
    
#     # Calculate the weighted score using the defined weights for each model
#     weighted_score = (0.5 * finbert_score) + (0.3 * roberta_score) + (0.2 * vader_weighted_score)
    
#     # Final sentiment label based on the weighted score
#     if weighted_score > 0.35:
#         label = 'Positive'
#     elif weighted_score < -0.35:
#         label = 'Negative'
#     else:
#         label = 'Neutral'
    
#     # Return final sentiment label and weighted score
#     return label, weighted_score

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol."""
#     try:
#         company = yf.Ticker(ticker)
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Extracting and cleaning data (filtering required data)
#         net_income = income_statement.loc['Net Income'].iloc[0]
#         total_debt = balance_sheet.loc['Total Debt'].iloc[0]
#         revenue = income_statement.loc['Total Revenue'].iloc[0]
#         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0]
        
#         financial_summary = {
#             "net_income": net_income,
#             "total_debt": total_debt,
#             "revenue": revenue,
#             "operating_cash_flow": operating_cash_flow
#         }
        
#         return financial_summary

#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {"error": str(e)}

# # ---------------------------
# # Analyze Financial Sentiment and Generate GPT-2 Summary
# # ---------------------------
# def analyze_financial_data(ticker):
#     financial_data = get_financial_statements(ticker)
#     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
#     # Example GPT-2 response generation
#     gpt2_prompt = f"Based on the following financial data, {sentiment} sentiment was detected. Provide a summary.\n"
#     gpt2_prompt += f"Revenue: {financial_data['revenue']}\nNet Income: {financial_data['net_income']}\nDebt: {financial_data['total_debt']}\nOperating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     # Using GPT-2 to summarize
#     gpt2_result = generate_gpt2(gpt2_prompt)
    
#     return {
#         "financial_summary": financial_data,
#         "sentiment": sentiment,
#         "sentiment_score": sentiment_score,
#         "explanation": gpt2_result
#     }

# def generate_gpt2(prompt):
#     """Simple mockup of GPT-2's response generation."""
#     # GPT-2 would generate a detailed response
#     return f"The sentiment is {prompt} because the company's revenue is increasing, and while their debt is high, their cash flow is strong."

# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # Define extract_company_and_ticker Function
# # ---------------------------
# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# # ---------------------------
# # API Endpoints (Preserved News Section)
# # ---------------------------
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; missing ticker'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}".'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         stock = yf.Ticker(ticker)
#         hist  = stock.history(period="1mo")
#         info  = stock.info

#         current_price   = hist['Close'].iloc[-1]
#         open_price      = hist['Open'].iloc[-1]
#         high_price      = hist['High'].iloc[-1]
#         low_price       = hist['Low'].iloc[-1]
#         previous_close  = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume          = hist['Volume'].iloc[-1]

#         sma_10          = hist['Close'].rolling(10).mean().iloc[-1]
#         trend           = "up" if current_price > sma_10 else "down"
#         price_change    = (current_price - previous_close) / previous_close
#         volatility      = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)

#         # original FinBERT-only sentiments
#         sentiments = analyze_sentiment(news_string)
#         overall_sentiment = sentiments[0]  # Sentiment from analyze_sentiment

#         # ─────────────── New: ensemble sentiment scores ───────────────
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })
#         # ────────────────────────────────────────────────────────────────

#         # Fetch financial statement sentiment
#         financial_sentiment_data = analyze_financial_data(ticker)
#         financial_sentiment = financial_sentiment_data['sentiment']
#         financial_statements_content = financial_sentiment_data['financial_summary']

#         # Rule-based decision
#         if trend == "up" and overall_sentiment == "Positive":
#             decision = "Buy"
#         elif trend == "down" and overall_sentiment == "Negative":
#             decision = "Sell"
#         else:
#             decision = "Hold"

#         analysis = (
#             f"Based on technical analysis, {ticker} is trading at ${current_price:.2f} ..."
#         )

#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_sentiment,
#             'financial_statements_content': financial_statements_content,
#             'analysis': analysis
#         }
#         return jsonify(response)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)


# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')

# # ─────────────────────────────────────────────────────────────────────────────
# # Correct import for the transformer pipeline
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ─────────────────────────────────────────────────────────────────────────────

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = "4c310cb414224d468ee9087dd9f208d6"  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Sentiment Analysis (FinBERT, RoBERTa, VADER)
# # ---------------------------
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Corrected pipeline import
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
    
#     # Sentiment from FinBERT
#     finbert_result = finbert(text)[0]
#     finbert_label = finbert_result['label']
#     finbert_score = finbert_result['score']
    
#     # Sentiment from RoBERTa
#     roberta_result = roberta(text)[0]
#     roberta_label = roberta_result['label']
#     roberta_score = roberta_result['score']
    
#     # Sentiment from VADER
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Map FinBERT result to score: Positive (1), Neutral (0), Negative (-1)
#     finbert_score = 1 if finbert_label == 'Positive' else -1 if finbert_label == 'Negative' else 0
    
#     # Map RoBERTa result to score: Positive (1), Neutral (0), Negative (-1)
#     roberta_score = roberta_score if roberta_label == 'POS' else -roberta_score if roberta_label == 'NEG' else 0
    
#     # VADER score is already a numeric value between -1 and 1 (no need for mapping)
#     vader_weighted_score = vader_score  # VADER score can directly be used for weighting
    
#     # Calculate the weighted score using the defined weights for each model
#     weighted_score = (0.5 * finbert_score) + (0.3 * roberta_score) + (0.2 * vader_weighted_score)
    
#     # Final sentiment label based on the weighted score
#     if weighted_score > 0.35:
#         label = 'Positive'
#     elif weighted_score < -0.35:
#         label = 'Negative'
#     else:
#         label = 'Neutral'
    
#     # Return final sentiment label and weighted score
#     return label, weighted_score

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# # def get_financial_statements(ticker):
# #     """Fetch the financial statements for a given US ticker symbol."""
# #     try:
# #         company = yf.Ticker(ticker)
# #         balance_sheet = company.balance_sheet
# #         income_statement = company.financials
# #         cashflow_statement = company.cashflow
        
# #         # Extracting and cleaning data (filtering required data)
# #         net_income = income_statement.loc['Net Income'].iloc[0]
# #         total_debt = balance_sheet.loc['Total Debt'].iloc[0]
# #         revenue = income_statement.loc['Total Revenue'].iloc[0]
# #         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0]
        
# #         financial_summary = {
# #             "net_income": net_income,
# #             "total_debt": total_debt,
# #             "revenue": revenue,
# #             "operating_cash_flow": operating_cash_flow
# #         }
        
# #         return financial_summary

# #     except Exception as e:
# #         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
# #         return {"error": str(e)}

# # # ---------------------------
# # # Analyze Financial Sentiment and Generate GPT-2 Summary
# # # ---------------------------
# # def analyze_financial_data(ticker):
# #     financial_data = get_financial_statements(ticker)
# #     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
    
# #     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
# #     # Example GPT-2 response generation
# #     gpt2_prompt = f"Based on the following financial data, {sentiment} sentiment was detected. Provide a summary.\n"
# #     gpt2_prompt += f"Revenue: {financial_data['revenue']}\nNet Income: {financial_data['net_income']}\nDebt: {financial_data['total_debt']}\nOperating Cash Flow: {financial_data['operating_cash_flow']}"
    
# #     # Using GPT-2 to summarize
# #     gpt2_result = generate_gpt2(gpt2_prompt)
    
# #     return {
# #         "financial_summary": financial_data,
# #         "sentiment": sentiment,
# #         "sentiment_score": sentiment_score,
# #         "explanation": gpt2_result
# #     }

# # def generate_gpt2(prompt):
# #     """Simple mockup of GPT-2's response generation."""
# #     # GPT-2 would generate a detailed response
# #     return f"The sentiment is {prompt} because the company's revenue is increasing, and while their debt is high, their cash flow is strong."

# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol."""
#     try:
#         company = yf.Ticker(ticker)
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Extracting and cleaning data (filtering required data)
#         net_income = income_statement.loc['Net Income'].iloc[0]
#         total_debt = balance_sheet.loc['Total Debt'].iloc[0]
#         revenue = income_statement.loc['Total Revenue'].iloc[0]
#         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0]
        
#         financial_summary = {
#             "net_income": net_income,
#             "total_debt": total_debt,
#             "revenue": revenue,
#             "operating_cash_flow": operating_cash_flow
#         }
        
#         return financial_summary

#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {"error": str(e)}

# # ---------------------------
# # Analyze Financial Sentiment and Generate GPT-2 Summary
# # ---------------------------
# def analyze_financial_data(ticker):
#     financial_data = get_financial_statements(ticker)
#     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
#     # Example GPT-2 response generation
#     gpt2_prompt = f"Based on the following financial data, {sentiment} sentiment was detected. Provide a summary.\n"
#     gpt2_prompt += f"Revenue: {financial_data['revenue']}\nNet Income: {financial_data['net_income']}\nDebt: {financial_data['total_debt']}\nOperating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     # Using GPT-2 to summarize
#     gpt2_result = generate_gpt2(gpt2_prompt)
    
#     return {
#         "financial_summary": financial_data,
#         "sentiment": sentiment,
#         "sentiment_score": sentiment_score,
#         "explanation": gpt2_result
#     }

# def generate_gpt2(prompt):
#     """Simple mockup of GPT-2's response generation."""
#     # GPT-2 would generate a detailed response
#     return f"The sentiment is {prompt} because the company's revenue is increasing, and while their debt is high, their cash flow is strong."


# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # Define extract_company_and_ticker Function
# # ---------------------------
# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# # ---------------------------
# # API Endpoints (Preserved News Section)
# # ---------------------------
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; missing ticker'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}".'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         stock = yf.Ticker(ticker)
#         hist  = stock.history(period="1mo")
#         info  = stock.info

#         current_price   = hist['Close'].iloc[-1]
#         open_price      = hist['Open'].iloc[-1]
#         high_price      = hist['High'].iloc[-1]
#         low_price       = hist['Low'].iloc[-1]
#         previous_close  = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume          = hist['Volume'].iloc[-1]

#         sma_10          = hist['Close'].rolling(10).mean().iloc[-1]
#         trend           = "up" if current_price > sma_10 else "down"
#         price_change    = (current_price - previous_close) / previous_close
#         volatility      = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)

#         # original FinBERT-only sentiments
#         sentiments = analyze_sentiment(news_string)
#         overall_sentiment = sentiments[0]  # Sentiment from analyze_sentiment

#         # ─────────────── New: ensemble sentiment scores ───────────────
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })
#         # ────────────────────────────────────────────────────────────────

#         # Fetch financial statement sentiment
#         financial_sentiment_data = analyze_financial_data(ticker)
#         financial_sentiment = financial_sentiment_data['sentiment']
#         financial_statements_content = financial_sentiment_data['financial_summary']

#         # Rule-based decision
#         if trend == "up" and overall_sentiment == "Positive":
#             decision = "Buy"
#         elif trend == "down" and overall_sentiment == "Negative":
#             decision = "Sell"
#         else:
#             decision = "Hold"

#         analysis = (
#             f"Based on technical analysis, {ticker} is trading at ${current_price:.2f} ..."
#         )

#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_sentiment,
#             'financial_statements_content': financial_statements_content,
#             'analysis': analysis
#         }
#         return jsonify(response)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)



# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')

# # ─────────────────────────────────────────────────────────────────────────────
# # Correct import for the transformer pipeline
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ─────────────────────────────────────────────────────────────────────────────

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = ""  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Sentiment Analysis (FinBERT, RoBERTa, VADER)
# # ---------------------------
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Corrected pipeline import
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
    
#     # Sentiment from FinBERT
#     finbert_result = finbert(text)[0]
#     finbert_label = finbert_result['label']
#     finbert_score = finbert_result['score']
    
#     # Sentiment from RoBERTa
#     roberta_result = roberta(text)[0]
#     roberta_label = roberta_result['label']
#     roberta_score = roberta_result['score']
    
#     # Sentiment from VADER
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Map FinBERT result to score: Positive (1), Neutral (0), Negative (-1)
#     finbert_score = 1 if finbert_label == 'Positive' else -1 if finbert_label == 'Negative' else 0
    
#     # Map RoBERTa result to score: Positive (1), Neutral (0), Negative (-1)
#     roberta_score = roberta_score if roberta_label == 'POS' else -roberta_score if roberta_label == 'NEG' else 0
    
#     # VADER score is already a numeric value between -1 and 1 (no need for mapping)
#     vader_weighted_score = vader_score  # VADER score can directly be used for weighting
    
#     # Calculate the weighted score using the defined weights for each model
#     weighted_score = (0.5 * finbert_score) + (0.3 * roberta_score) + (0.2 * vader_weighted_score)
    
#     # Final sentiment label based on the weighted score
#     if weighted_score > 0.35:
#         label = 'Positive'
#     elif weighted_score < -0.35:
#         label = 'Negative'
#     else:
#         label = 'Neutral'
    
#     # Return final sentiment label and weighted score
#     return label, weighted_score

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol."""
#     try:
#         company = yf.Ticker(ticker)
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Extracting and cleaning data (filtering required data)
#         net_income = income_statement.loc['Net Income'].iloc[0]
#         total_debt = balance_sheet.loc['Total Debt'].iloc[0]
#         revenue = income_statement.loc['Total Revenue'].iloc[0]
#         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0]
        
#         financial_summary = {
#             "net_income": net_income,
#             "total_debt": total_debt,
#             "revenue": revenue,
#             "operating_cash_flow": operating_cash_flow
#         }
        
#         # Return the financial summary as a formatted string for the response
#         financial_summary_str = f"Revenue: {revenue}\nNet Income: {net_income}\nDebt: {total_debt}\nOperating Cash Flow: {operating_cash_flow}"
        
#         return financial_summary, financial_summary_str

#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {"error": str(e)}, ""

# # ---------------------------
# # Analyze Financial Sentiment and Generate GPT-2 Summary
# # ---------------------------
# def analyze_financial_data(ticker):
#     financial_data, financial_summary_str = get_financial_statements(ticker)
#     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
#     return {
#         "financial_summary": financial_data,
#         "financial_summary_str": financial_summary_str,  # Add the string version for display
#         "sentiment": sentiment,
#         "sentiment_score": sentiment_score
#     }

# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # Define extract_company_and_ticker Function
# # ---------------------------
# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# # ---------------------------
# # API Endpoints (Preserved News Section)
# # ---------------------------
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; missing ticker'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}".'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         stock = yf.Ticker(ticker)
#         hist  = stock.history(period="1mo")
#         info  = stock.info

#         current_price   = hist['Close'].iloc[-1]
#         open_price      = hist['Open'].iloc[-1]
#         high_price      = hist['High'].iloc[-1]
#         low_price       = hist['Low'].iloc[-1]
#         previous_close  = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume          = hist['Volume'].iloc[-1]

#         sma_10          = hist['Close'].rolling(10).mean().iloc[-1]
#         trend           = "up" if current_price > sma_10 else "down"
#         price_change    = (current_price - previous_close) / previous_close
#         volatility      = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)

#         # original FinBERT-only sentiments
#         sentiments = analyze_sentiment(news_string)
#         overall_sentiment = sentiments[0]  # Sentiment from analyze_sentiment

#         # ─────────────── New: ensemble sentiment scores ───────────────
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })
#         # ────────────────────────────────────────────────────────────────

#         # Fetch financial statement sentiment
#         financial_sentiment_data = analyze_financial_data(ticker)
#         financial_sentiment = financial_sentiment_data['sentiment']
#         financial_statements_content = financial_sentiment_data['financial_summary_str']  # Get the string version

#         # Rule-based decision
#         if trend == "up" and overall_sentiment == "Positive":
#             decision = "Buy"
#         elif trend == "down" and overall_sentiment == "Negative":
#             decision = "Sell"
#         else:
#             decision = "Hold"

#         analysis = (
#             f"Based on technical analysis, {ticker} is trading at ${current_price:.2f} ..."
#         )

#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_sentiment,
#             'financial_statements_content': financial_statements_content,  # Displaying content here
#             'analysis': analysis
#         }
#         return jsonify(response)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)


# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')

# # ─────────────────────────────────────────────────────────────────────────────
# # Correct import for the transformer pipeline
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ─────────────────────────────────────────────────────────────────────────────

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = ""  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Sentiment Analysis (FinBERT, RoBERTa, VADER)
# # ---------------------------
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Corrected pipeline import
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
    
#     # Sentiment from FinBERT
#     finbert_result = finbert(text)[0]
#     finbert_label = finbert_result['label']
#     finbert_score = finbert_result['score']
    
#     # Sentiment from RoBERTa
#     roberta_result = roberta(text)[0]
#     roberta_label = roberta_result['label']
#     roberta_score = roberta_result['score']
    
#     # Sentiment from VADER
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Map FinBERT result to score: Positive (1), Neutral (0), Negative (-1)
#     finbert_score = 1 if finbert_label == 'Positive' else -1 if finbert_label == 'Negative' else 0
    
#     # Map RoBERTa result to score: Positive (1), Neutral (0), Negative (-1)
#     roberta_score = roberta_score if roberta_label == 'POS' else -roberta_score if roberta_label == 'NEG' else 0
    
#     # VADER score is already a numeric value between -1 and 1 (no need for mapping)
#     vader_weighted_score = vader_score  # VADER score can directly be used for weighting
    
#     # Calculate the weighted score using the defined weights for each model
#     weighted_score = (0.5 * finbert_score) + (0.3 * roberta_score) + (0.2 * vader_weighted_score)
    
#     # Final sentiment label based on the weighted score
#     if weighted_score > 0.15:
#         label = 'Positive'
#     elif weighted_score < -0.15:
#         label = 'Negative'
#     else:
#         label = 'Neutral'
    
#     # Return final sentiment label and weighted score
#     return label, weighted_score

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol for the last 3 years."""
#     try:
#         company = yf.Ticker(ticker)
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Extracting data for the last 3 years (if available)
#         net_income = income_statement.loc['Net Income'].iloc[0:3]
#         total_debt = balance_sheet.loc['Total Debt'].iloc[0:3]
#         revenue = income_statement.loc['Total Revenue'].iloc[0:3]
#         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0:3]
        
#         financial_summary = {
#             "net_income": net_income.tolist(),
#             "total_debt": total_debt.tolist(),
#             "revenue": revenue.tolist(),
#             "operating_cash_flow": operating_cash_flow.tolist()
#         }
        
#         financial_summary_str = f"Revenue: {revenue}\nNet Income: {net_income}\nDebt: {total_debt}\nOperating Cash Flow: {operating_cash_flow}"
        
#         return financial_summary, financial_summary_str

#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {"error": str(e)}, ""

# # ---------------------------
# # Analyze Financial Sentiment and Generate GPT-2 Summary
# # ---------------------------
# def analyze_financial_data(ticker):
#     financial_data, financial_summary_str = get_financial_statements(ticker)
#     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
#     gpt2_prompt = f"Based on the following financial data, {sentiment} sentiment was detected. Provide a summary.\n"
#     gpt2_prompt += f"Revenue: {financial_data['revenue']}\nNet Income: {financial_data['net_income']}\nDebt: {financial_data['total_debt']}\nOperating Cash Flow: {financial_data['operating_cash_flow']}"
    
#     gpt2_result = generate_gpt2(gpt2_prompt)
    
#     return {
#         "financial_summary": financial_data,
#         "financial_summary_str": financial_summary_str,  # Add the string version for display
#         "sentiment": sentiment,
#         "sentiment_score": sentiment_score,
#         "explanation": gpt2_result
#     }

# def generate_gpt2(prompt):
#     """Simple mockup of GPT-2's response generation."""
#     # GPT-2 would generate a detailed response
#     return f"The sentiment is {prompt} because the company's revenue is increasing, and while their debt is high, their cash flow is strong."

# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # Define extract_company_and_ticker Function
# # ---------------------------
# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# # ---------------------------
# # API Endpoints (Preserved News Section)
# # ---------------------------
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; missing ticker'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}".'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         stock = yf.Ticker(ticker)
#         hist  = stock.history(period="1mo")
#         info  = stock.info

#         current_price   = hist['Close'].iloc[-1]
#         open_price      = hist['Open'].iloc[-1]
#         high_price      = hist['High'].iloc[-1]
#         low_price       = hist['Low'].iloc[-1]
#         previous_close  = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume          = hist['Volume'].iloc[-1]

#         sma_10          = hist['Close'].rolling(10).mean().iloc[-1]
#         trend           = "up" if current_price > sma_10 else "down"
#         price_change    = (current_price - previous_close) / previous_close
#         volatility      = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)

#         # original FinBERT-only sentiments
#         sentiments = analyze_sentiment(news_string)
#         overall_sentiment = sentiments[0]  # Sentiment from analyze_sentiment

#         # ─────────────── New: ensemble sentiment scores ───────────────
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })
#         # ────────────────────────────────────────────────────────────────

#         # Fetch financial statement sentiment
#         financial_sentiment_data = analyze_financial_data(ticker)
#         financial_sentiment = financial_sentiment_data['sentiment']
#         financial_statements_content = financial_sentiment_data['financial_summary_str']  # Get the string version

#         # Rule-based decision
#         if trend == "up" and overall_sentiment == "Positive":
#             decision = "Buy"
#         elif trend == "down" and overall_sentiment == "Negative":
#             decision = "Sell"
#         else:
#             decision = "Hold"

#         analysis = (
#             f"Based on technical analysis, {ticker} is trading at ${current_price:.2f} ..."
#         )

#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_sentiment,
#             'financial_statements_content': financial_statements_content,  # Displaying content here
#             'analysis': analysis
#         }
#         return jsonify(response)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)


# import os
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import yfinance as yf
# import numpy as np
# from datetime import datetime, timedelta
# import requests
# import re
# from bs4 import BeautifulSoup
# import nltk
# nltk.download('vader_lexicon')
# from transformers import pipeline as _hf_pipeline
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from typing import Dict, List

# app = Flask(__name__)
# CORS(app)

# # ---------------------------
# # Configuration & Global Variables
# # ---------------------------
# NEWSAPI_KEY = ""  # Replace with your actual NewsAPI key.

# SUPPORTED_TICKERS = [
#     'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
#     'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
#     'TSLA', 'F', 'COIN', 'MRNA'
# ]

# SECTOR_MAP = {
#     'AAPL': 'tech', 'MSFT': 'tech', 'NVDA': 'tech', 'AMD': 'tech',
#     'JNJ': 'healthcare', 'PFE': 'healthcare', 'JPM': 'financial', 'GS': 'financial',
#     'KO': 'consumer', 'PEP': 'consumer', 'XOM': 'energy', 'NEE': 'utilities',
#     'CVX': 'energy', 'WMT': 'retail', 'HD': 'retail', 'GME': 'retail',
#     'TSLA': 'auto', 'F': 'auto', 'COIN': 'crypto', 'MRNA': 'biotech'
# }

# COMPANY_NAME_TO_TICKER = {
#     'apple': 'AAPL',
#     'microsoft': 'MSFT',
#     'nvda': 'NVDA',
#     'amd': 'AMD',
#     'jnj': 'JNJ',
#     'pfe': 'PFE',
#     'jpm': 'JPM',
#     'gs': 'GS',
#     'ko': 'KO',
#     'pep': 'PEP',
#     'xom': 'XOM',
#     'nee': 'NEE',
#     'cvx': 'CVX',
#     'wmt': 'WMT',
#     'hd': 'HD',
#     'gme': 'GME',
#     'tsla': 'TSLA',
#     'f': 'F',
#     'coin': 'COIN',
#     'mrna': 'MRNA'
# }

# RISK_LEVELS = {
#     'low': ['JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 'XOM', 'CVX', 'WMT', 'NEE'],
#     'medium': ['AAPL', 'MSFT', 'HD', 'F', 'AMD'],
#     'high': ['NVDA', 'TSLA', 'GME', 'COIN', 'MRNA']
# }

# user_profile = {
#     'available_amount': 5000.0,
#     'risk_preference': 'medium'
# }

# # ---------------------------
# # Sentiment Analysis (FinBERT, RoBERTa, VADER)
# # ---------------------------
# finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Corrected pipeline import
# roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# vader = SentimentIntensityAnalyzer()

# def analyze_sentiment(text):
#     """Fixed-weight ensemble sentiment analysis using FinBERT, RoBERTa, and VADER."""
    
#     # Sentiment from FinBERT
#     finbert_result = finbert(text)[0]
#     finbert_label = finbert_result['label']
#     finbert_score = finbert_result['score']
    
#     # Sentiment from RoBERTa
#     roberta_result = roberta(text)[0]
#     roberta_label = roberta_result['label']
#     roberta_score = roberta_result['score']
    
#     # Sentiment from VADER
#     vader_score = vader.polarity_scores(text)['compound']
    
#     # Map FinBERT result to score: Positive (1), Neutral (0), Negative (-1)
#     finbert_score = 1 if finbert_label == 'Positive' else -1 if finbert_label == 'Negative' else 0
    
#     # Map RoBERTa result to score: Positive (1), Neutral (0), Negative (-1)
#     roberta_score = roberta_score if roberta_label == 'POS' else -roberta_score if roberta_label == 'NEG' else 0
    
#     # VADER score is already a numeric value between -1 and 1 (no need for mapping)
#     vader_weighted_score = vader_score  # VADER score can directly be used for weighting
    
#     # Calculate the weighted score using the defined weights for each model
#     weighted_score = (0.5 * finbert_score) + (0.3 * roberta_score) + (0.2 * vader_weighted_score)
    
#     # Final sentiment label based on the weighted score
#     if weighted_score > 0.15:
#         label = 'Positive'
#     elif weighted_score < -0.15:
#         label = 'Negative'
#     else:
#         label = 'Neutral'
    
#     # Return final sentiment label and weighted score
#     return label, weighted_score

# # ---------------------------
# # Financial Analysis Engine
# # ---------------------------
# class FinancialAnalyzer:
#     @staticmethod
#     def analyze_trend(values: List[float]) -> str:
#         """Deterministic trend analysis with percentages"""
#         if len(values) < 2:  # Handle case with insufficient data
#             return "insufficient data"
            
#         change_pct = (values[0] - values[-1]) / values[-1]  # Latest vs oldest
#         abs_change = abs(change_pct)
        
#         if abs_change < 0.05:
#             trend = "stable"
#         elif change_pct > 0:
#             trend = "growing" if abs_change > 0.1 else "slightly growing"
#         else:
#             trend = "declining" if abs_change > 0.1 else "slightly declining"
        
#         return f"{trend} ({change_pct:+.1%})"

#     @staticmethod
#     def generate_insights(financial_data: Dict[str, List[float]]) -> Dict[str, str]:
#         """Generate guaranteed structured insights"""
#         insights = {
#             "revenue_trend": FinancialAnalyzer.analyze_trend(financial_data['revenue']),
#             "profitability_trend": FinancialAnalyzer.analyze_trend(financial_data['net_income']),
#             "debt_trend": FinancialAnalyzer.analyze_trend(financial_data['total_debt']),
#             "cashflow_trend": FinancialAnalyzer.analyze_trend(financial_data['operating_cash_flow']),
#             "latest_revenue": f"${financial_data['revenue'][0]/1e9:.1f}B",
#             "latest_net_income": f"${financial_data['net_income'][0]/1e9:.1f}B"
#         }
        
#         # Generate summary text
#         insights['summary'] = (
#             f"Revenue is {insights['revenue_trend']}. "
#             f"Profits are {insights['profitability_trend']}. "
#             f"Debt is {insights['debt_trend']}. "
#             f"Cash flow is {insights['cashflow_trend']}."
#         )
        
#         return insights

# # ---------------------------
# # Financial Statement Functions
# # ---------------------------
# def get_financial_statements(ticker):
#     """Fetch the financial statements for a given US ticker symbol for the last 3 years."""
#     try:
#         company = yf.Ticker(ticker)
#         balance_sheet = company.balance_sheet
#         income_statement = company.financials
#         cashflow_statement = company.cashflow
        
#         # Extracting data for the last 3 years (if available)
#         net_income = income_statement.loc['Net Income'].iloc[0:3]
#         total_debt = balance_sheet.loc['Total Debt'].iloc[0:3]
#         revenue = income_statement.loc['Total Revenue'].iloc[0:3]
#         operating_cash_flow = cashflow_statement.loc['Operating Cash Flow'].iloc[0:3]
        
#         financial_summary = {
#             "net_income": net_income.tolist(),
#             "total_debt": total_debt.tolist(),
#             "revenue": revenue.tolist(),
#             "operating_cash_flow": operating_cash_flow.tolist()
#         }
        
#         financial_summary_str = f"Revenue: {revenue}\nNet Income: {net_income}\nDebt: {total_debt}\nOperating Cash Flow: {operating_cash_flow}"
        
#         return financial_summary, financial_summary_str

#     except Exception as e:
#         logging.error(f"Error fetching financial data for {ticker}: {str(e)}")
#         return {"error": str(e)}, ""

# def analyze_financial_data(ticker):
#     """Enhanced financial analysis with reliable insights"""
#     financial_data, financial_summary_str = get_financial_statements(ticker)
    
#     # Original sentiment analysis
#     sentiment_text = f"Revenue: {financial_data['revenue']}, Debt: {financial_data['total_debt']}, Net Income: {financial_data['net_income']}, Operating Cash Flow: {financial_data['operating_cash_flow']}"
#     sentiment, sentiment_score = analyze_sentiment(sentiment_text)
    
#     # New reliable insights
#     insights = FinancialAnalyzer.generate_insights(financial_data)
    
#     return {
#         "financial_summary": financial_data,
#         "financial_summary_str": financial_summary_str,
#         "sentiment": sentiment,
#         "sentiment_score": round(sentiment_score, 2),
#         "fundamental_insights": insights
#     }

# # ---------------------------
# # News Fetching Functions
# # ---------------------------
# def google_query(search_term):
#     if "news" not in search_term.lower():
#         search_term += " stock news"
#     url = f"https://www.google.com/search?q={search_term}&tbm=nws"
#     return re.sub(r"\s", "+", url)

# def google_scrape_news(company_name):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
#     }
#     query = company_name + " stock news"
#     search_url = google_query(query)
#     try:
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
#         html = response.text
#     except Exception as e:
#         app.logger.error(f"Error fetching news from Google: {e}")
#         return [], "Recent News:\nNo news available."
    
#     soup = BeautifulSoup(html, "html.parser")
#     headlines = []
#     for tag in soup.find_all("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"}):
#         headline = tag.get_text().strip()
#         if headline and headline not in headlines:
#             headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"}):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if not headlines:
#         for tag in soup.find_all("div", class_=lambda c: c and "DY5T1d" in c):
#             headline = tag.get_text().strip()
#             if headline and headline not in headlines:
#                 headlines.append(headline)
#     if len(headlines) > 4:
#         headlines = headlines[:4]
#     news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# def get_news_from_newsapi(company_name):
#     if not NEWSAPI_KEY:
#         app.logger.error("NEWSAPI_KEY is not provided.")
#         return [], ""
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": company_name + " stock",
#         "sortBy": "publishedAt",
#         "apiKey": NEWSAPI_KEY,
#         "language": "en",
#         "pageSize": 4
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]
#         if headlines:
#             news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#             return headlines, news_string
#     except Exception as e:
#         app.logger.error(f"NewsAPI error: {e}")
#     return [], ""

# def get_recent_stock_news(company_name, ticker):
#     stock = yf.Ticker(ticker)
#     try:
#         news_items = stock.news
#     except Exception:
#         news_items = []
#     headlines = []
#     if news_items:
#         for item in news_items:
#             if "title" in item and item["title"]:
#                 headlines.append(item["title"])
#     if not headlines:
#         headlines, news_string = get_news_from_newsapi(company_name)
#         if not headlines:
#             headlines, news_string = google_scrape_news(company_name)
#     else:
#         news_string = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
#     return headlines, news_string

# # ---------------------------
# # Company/Ticker Extraction
# # ---------------------------
# def extract_company_and_ticker(query):
#     q_stripped = query.strip()
#     q_upper = q_stripped.upper()
#     if q_upper in SUPPORTED_TICKERS:
#         return q_upper, q_upper
#     query_lower = q_stripped.lower()
#     for company, ticker in COMPANY_NAME_TO_TICKER.items():
#         if company in query_lower:
#             return company.capitalize(), ticker
#     return None, None

# def generate_decision(trend: str, confidence: float, news_sentiment: str, financial_insights: dict) -> dict:
#     """Enhanced decision logic with financial insights"""
#     # Basic rules
#     if trend == "up" and news_sentiment == "Positive":
#         action = "Buy"
#         reasoning = "Strong technical uptrend with positive news sentiment"
#     elif trend == "down" and news_sentiment == "Negative":
#         action = "Sell" 
#         reasoning = "Downtrend confirmed with negative news sentiment"
#     else:
#         action = "Hold"
#         reasoning = "Mixed signals - requires further analysis"

#     # Enhance with financial insights
#     if "declining" in financial_insights['profitability_trend'] and action == "Buy":
#         action = "Hold"
#         reasoning += ", but profits are declining"
#     elif "growing" in financial_insights['revenue_trend'] and action == "Hold":
#         reasoning += ", though revenue is growing"
    
#     return {
#         'action': action,
#         'reasoning': reasoning + f". Fundamentals: {financial_insights['summary']}"
#     }

# # ---------------------------
# # API Endpoints
# # ---------------------------
# @app.route('/api/stocks', methods=['GET'])
# def get_supported_stocks():
#     return jsonify({
#         'tickers': SUPPORTED_TICKERS,
#         'risk_levels': list(RISK_LEVELS.keys()),
#         'sectors': list(set(SECTOR_MAP.values()))
#     })

# @app.route('/api/analyze', methods=['GET'])
# def analyze_stock():
#     ticker = request.args.get('ticker', '').upper()
#     if not ticker:
#         full_query = request.args.get('query', '')
#         _, extracted_ticker = extract_company_and_ticker(full_query)
#         if extracted_ticker:
#             ticker = extracted_ticker.upper()
#         else:
#             return jsonify({'error': 'Invalid query; missing ticker'}), 400

#     if ticker not in SUPPORTED_TICKERS:
#         return jsonify({'error': f'Invalid ticker "{ticker}".'}), 400

#     amount = float(request.args.get('amount', user_profile['available_amount']))
    
#     try:
#         # Technical Analysis
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1mo")
#         info = stock.info

#         current_price = hist['Close'].iloc[-1]
#         open_price = hist['Open'].iloc[-1]
#         high_price = hist['High'].iloc[-1]
#         low_price = hist['Low'].iloc[-1]
#         previous_close = hist['Close'].iloc[-2] if len(hist)>1 else current_price
#         volume = hist['Volume'].iloc[-1]

#         sma_10 = hist['Close'].rolling(10).mean().iloc[-1]
#         trend = "up" if current_price > sma_10 else "down"
#         price_change = (current_price - previous_close) / previous_close
#         volatility = (high_price - low_price) / open_price

#         confidence = 0.5
#         if trend == "up":
#             confidence += 0.2
#         confidence += min(0.2, max(-0.2, price_change*10))
#         confidence -= min(0.1, volatility*0.5)
#         confidence = min(0.95, max(0.05, confidence))

#         shares_possible = int(amount / current_price) if amount > 0 else 0

#         # News Analysis
#         company_name, _ = extract_company_and_ticker(ticker)
#         news_list, news_string = get_recent_stock_news(company_name or ticker, ticker)
#         overall_sentiment, news_sentiment_score = analyze_sentiment(news_string)
        
#         detailed_sentiments = []
#         for hl in news_list:
#             label, score = analyze_sentiment(hl)
#             detailed_sentiments.append({
#                 'headline': hl,
#                 'label': label,
#                 'score': round(score, 2)
#             })

#         # Financial Analysis
#         financial_data = analyze_financial_data(ticker)
#         financial_insights = financial_data['fundamental_insights']

#         # Generate Decision
#         decision = generate_decision(
#             trend=trend,
#             confidence=confidence,
#             news_sentiment=overall_sentiment,
#             financial_insights=financial_insights
#         )

#         # Prepare Response
#         response = {
#             'ticker': ticker,
#             'current_price': round(current_price, 2),
#             'open_price': round(open_price, 2),
#             'high_price': round(high_price, 2),
#             'low_price': round(low_price, 2),
#             'previous_close': round(previous_close, 2),
#             'volume': int(volume),
#             'sma_10': round(sma_10, 2),
#             'pe_ratio': info.get('trailingPE'),
#             'dividend_yield': info.get('dividendYield', 0),
#             'price_change_pct': round(price_change * 100, 2),
#             'volatility_pct': round(volatility * 100, 2),
#             'trend': trend,
#             'technical_confidence': round(confidence, 2),
#             'shares_possible': shares_possible,
#             'news': news_string,
#             'overall_news_sentiment': overall_sentiment,
#             'detailed_sentiments': detailed_sentiments,
#             'financial_statements_sentiment': financial_data['sentiment'],
#             'financial_statements_content': financial_data['financial_summary_str'],
#             'fundamental_insights': financial_insights,
#             'decision': decision['action'],
#             'analysis': decision['reasoning']
#         }
#         return jsonify(response)

#     except Exception as e:
#         logging.error(f"Analysis error: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)



import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup
import nltk
nltk.download('vader_lexicon')
from transformers import pipeline as _hf_pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict, List, Tuple

app = Flask(__name__)
CORS(app)

# ---------------------------
# Configuration & Globals
# ---------------------------
NEWSAPI_KEY = "4c310cb414224d468ee9087dd9f208d6"

SUPPORTED_TICKERS = [
    'AAPL','MSFT','NVDA','AMD','JNJ','PFE','JPM','GS',
    'KO','PEP','XOM','NEE','CVX','WMT','HD','GME',
    'TSLA','F','COIN','MRNA'
]

SECTOR_MAP = {
    'AAPL':'tech','MSFT':'tech','NVDA':'tech','AMD':'tech',
    'JNJ':'healthcare','PFE':'healthcare','JPM':'financial','GS':'financial',
    'KO':'consumer','PEP':'consumer','XOM':'energy','NEE':'utilities',
    'CVX':'energy','WMT':'retail','HD':'retail','GME':'retail',
    'TSLA':'auto','F':'auto','COIN':'crypto','MRNA':'biotech'
}

COMPANY_NAME_TO_TICKER = {
    'apple':'AAPL','microsoft':'MSFT','nvidia':'NVDA','amd':'AMD',
    'johnson & johnson':'JNJ','jnj':'JNJ','pfizer':'PFE','jpmorgan':'JPM',
    'goldman sachs':'GS','coca cola':'KO','pepsi':'PEP','exxon':'XOM',
    'next era energy':'NEE','chevron':'CVX','walmart':'WMT','home depot':'HD',
    'gamestop':'GME','tesla':'TSLA','ford':'F','coinbase':'COIN','moderna':'MRNA',
    'appl':'AAPL','micro':'MSFT','nvdia':'NVDA','xoom':'XOM','wallmart':'WMT',
    'tesa':'TSLA','ford motor':'F','coin base':'COIN','modern':'MRNA'
}
_normalized_company_map = {
    re.sub(r'[^a-z0-9\s]','',k):v for k,v in COMPANY_NAME_TO_TICKER.items()
}

RISK_LEVELS = {
    'low':['JNJ','PFE','JPM','GS','KO','PEP','XOM','CVX','WMT','NEE'],
    'medium':['AAPL','MSFT','HD','F','AMD'],
    'high':['NVDA','TSLA','GME','COIN','MRNA']
}

RISK_BASED_RECOMMENDATIONS = {
    'low': [
        {'ticker':'JNJ','allocation':0.30,'reason':'Stable healthcare dividends'},
        {'ticker':'KO','allocation':0.25,'reason':'Consumer staple'},
        {'ticker':'WMT','allocation':0.25,'reason':'Resilient retail'},
        {'ticker':'NEE','allocation':0.20,'reason':'Renewables utility'}
    ],
    'medium': [
        {'ticker':'AAPL','allocation':0.35,'reason':'Tech ecosystem'},
        {'ticker':'MSFT','allocation':0.35,'reason':'Cloud leader'},
        {'ticker':'JPM','allocation':0.20,'reason':'Banking stability'},
        {'ticker':'HD','allocation':0.10,'reason':'Home improvement'}
    ],
    'high': [
        {'ticker':'NVDA','allocation':0.40,'reason':'AI/GPU growth'},
        {'ticker':'TSLA','allocation':0.30,'reason':'EV upside'},
        {'ticker':'MRNA','allocation':0.20,'reason':'mRNA biotech'},
        {'ticker':'COIN','allocation':0.10,'reason':'Crypto exposure'}
    ]
}

user_profile = {'available_amount':5000.0,'risk_preference':'medium'}

# ---------------------------
# Sentiment Analysis
# ---------------------------
finbert = _hf_pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
roberta = _hf_pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
vader = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> Tuple[str, float]:
    try:
        fb = finbert(text)[0]
        fb_score = 1 if fb['label']=='Positive' else -1 if fb['label']=='Negative' else 0
        rb = roberta(text)[0]
        rb_score = rb['score'] if rb['label']=='POS' else -rb['score'] if rb['label']=='NEG' else 0
        vd = vader.polarity_scores(text)['compound']
        score = 0.5*fb_score + 0.3*rb_score + 0.2*vd
        if score > 0.15: return 'Positive', score
        if score < -0.15: return 'Negative', score
        return 'Neutral', score
    except:
        return 'Neutral', 0.0

# ---------------------------
# Financial Analysis
# ---------------------------
class FinancialAnalyzer:
    @staticmethod
    def analyze_trend(vals: List[float]) -> str:
        if len(vals) < 2: return "insufficient data"
        change = (vals[0] - vals[-1]) / vals[-1]
        pct = abs(change)
        if pct < 0.05:
            trend = "stable"
        elif change > 0:
            trend = "growing" if pct > 0.1 else "slightly growing"
        else:
            trend = "declining" if pct > 0.1 else "slightly declining"
        return f"{trend} ({change:+.1%})"

    @staticmethod
    def generate_insights(data: Dict[str, List[float]]) -> Dict[str, str]:
        insights = {
            'revenue_trend': FinancialAnalyzer.analyze_trend(data['revenue']),
            'profitability_trend': FinancialAnalyzer.analyze_trend(data['net_income']),
            'debt_trend': FinancialAnalyzer.analyze_trend(data['total_debt']),
            'cashflow_trend': FinancialAnalyzer.analyze_trend(data['operating_cash_flow']),
            'latest_revenue': f"${data['revenue'][0]/1e9:.1f}B",
            'latest_net_income': f"${data['net_income'][0]/1e9:.1f}B"
        }
        insights['summary'] = (
            f"Revenue is {insights['revenue_trend']}. "
            f"Profits are {insights['profitability_trend']}. "
            f"Debt is {insights['debt_trend']}. "
            f"Cash flow is {insights['cashflow_trend']}."
        )
        return insights

def get_financial_statements(ticker: str) -> Tuple[Dict[str, List[float]], str]:
    try:
        c = yf.Ticker(ticker)
        fin, bal, cf = c.financials, c.balance_sheet, c.cashflow
        ni  = fin.loc['Net Income'].iloc[:3].tolist()
        td  = bal.loc['Total Debt'].iloc[:3].tolist()
        rv  = fin.loc['Total Revenue'].iloc[:3].tolist()
        ocf = cf.loc['Operating Cash Flow'].iloc[:3].tolist()
        summary = f"Revenue: {rv}\nNet Income: {ni}\nDebt: {td}\nOperating CF: {ocf}"
        return {'net_income':ni,'total_debt':td,'revenue':rv,'operating_cash_flow':ocf}, summary
    except:
        return {'net_income':[],'total_debt':[],'revenue':[],'operating_cash_flow':[]}, ''

def analyze_financial_data(ticker: str) -> Dict:
    data, summary = get_financial_statements(ticker)
    txt = f"Revenue:{data['revenue']},Debt:{data['total_debt']},NI:{data['net_income']},OCF:{data['operating_cash_flow']}"
    sent, _ = analyze_sentiment(txt)
    insights = FinancialAnalyzer.generate_insights(data)
    return {
        'financial_summary': data,
        'financial_summary_str': summary,
        'sentiment': sent,
        'fundamental_insights': insights
    }

# ---------------------------
# News Fetching
# ---------------------------
def google_query(q: str) -> str:
    if 'news' not in q.lower():
        q += ' stock news'
    return f"https://www.google.com/search?q={'+'.join(q.split())}&tbm=nws"

def google_scrape_news(name: str) -> Tuple[List[str], str]:
    try:
        r = requests.get(google_query(name), headers={'User-Agent':'Mozilla/5.0'}, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        heads = [t.get_text().strip() for t in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')][:4]
    except:
        heads = []
    s = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(heads))
    return heads, s

def get_news_from_newsapi(name: str) -> Tuple[List[str], str]:
    if not NEWSAPI_KEY:
        return [], ''
    params = {'q': f"{name} stock", 'apiKey': NEWSAPI_KEY, 'pageSize': 4}
    try:
        js = requests.get("https://newsapi.org/v2/everything", params=params, timeout=5).json()
        heads = [a['title'] for a in js.get('articles', [])][:4]
        s = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(heads))
        return heads, s
    except:
        return [], ''

def get_recent_stock_news(name: str, ticker: str) -> Tuple[List[str], str]:
    try:
        yf_news = yf.Ticker(ticker).news or []
        heads = [i['title'] for i in yf_news if i.get('title')][:4]
    except:
        heads = []
    if not heads:
        heads, s = get_news_from_newsapi(name)
        if not heads:
            heads, s = google_scrape_news(name)
    else:
        s = "Recent News:\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(heads))
    return heads, s

# ---------------------------
# Extraction & Decision
# ---------------------------
def extract_company_and_ticker(q: str) -> Tuple[str, str]:
    clean = re.sub(r'[^a-z0-9\s]', '', q.lower())
    for w in clean.split():
        if w.upper() in SUPPORTED_TICKERS:
            return w.upper(), w.upper()
    for k, v in _normalized_company_map.items():
        if k and k in clean:
            return k, v
    return None, None


def perform_analysis(ticker: str, amount: float) -> Dict:
    try:
        st = yf.Ticker(ticker)
        h  = st.history(period='1mo')
        cp, op, hi, lo = h['Close'].iloc[-1], h['Open'].iloc[-1], h['High'].iloc[-1], h['Low'].iloc[-1]
        prev           = h['Close'].iloc[-2] if len(h)>1 else cp
        vol            = int(h['Volume'].iloc[-1])
        sma10          = h['Close'].rolling(10).mean().iloc[-1]

        trend      = 'up' if cp > sma10 else 'down'
        change_pct = (cp - prev) / prev
        volatility = (hi - lo) / op if op else 0

        confidence = min(
            0.95,
            max(
                0.05,
                0.5
                + (0.2 if trend == 'up' else -0.2)
                + min(0.2, max(-0.2, change_pct * 10))
                - min(0.1, volatility * 0.5)
            )
        )
        shares = int(amount / cp) if amount > 0 else 0

        name = next((k for k, v in COMPANY_NAME_TO_TICKER.items() if v == ticker), ticker)
        news_list, news_str = get_recent_stock_news(name.capitalize(), ticker)
        overall_sent, _    = analyze_sentiment(news_str)

        fin     = analyze_financial_data(ticker)
        fin_ins = fin['fundamental_insights']
        dec     = generate_decision(trend, confidence, overall_sent, fin_ins)

        return {
            'ticker': ticker,
            'current_price': round(cp, 2),
            'open_price': round(op, 2),
            'high_price': round(hi, 2),
            'low_price': round(lo, 2),
            'previous_close': round(prev, 2),
            'volume': vol,
            'sma_10': round(sma10, 2),
            'price_change_pct': round(change_pct * 100, 2),
            'volatility_pct': round(volatility * 100, 2),
            'trend': trend,
            'confidence': round(confidence, 2),
            'technical_confidence': round(confidence, 2),   # <-- added
            'shares_possible': shares,
            'pe_ratio': st.info.get('trailingPE'),
            'dividend_yield': st.info.get('dividendYield', 0),
            'news': news_str,
            'overall_news_sentiment': overall_sent,
            'financial_statements_sentiment': fin['sentiment'],
            'financial_statements_content': fin['financial_summary_str'],
            'fundamental_insights': fin_ins,
            'decision': dec['action'],
            'analysis': dec['reasoning']
        }

    except Exception as e:
        logging.error(f"Analysis error for {ticker}: {e}")
        return {'error': str(e)}

# ---------------------------
# API Endpoints
# ---------------------------
@app.route('/api/stocks', methods=['GET'])
def supported_stocks():
    return jsonify({
        'tickers': SUPPORTED_TICKERS,
        'sectors': SECTOR_MAP,
        'risk_levels': list(RISK_LEVELS.keys())
    })

@app.route('/api/analyze', methods=['GET'])
def analyze_endpoint():
    raw_t = request.args.get('ticker','').strip()
    qry   = request.args.get('query','').strip()
    amt   = float(request.args.get('amount', user_profile['available_amount']))

    if raw_t and raw_t.upper() not in SUPPORTED_TICKERS:
        qry, raw_t = raw_t, ''

    # Static trigger for recommendations
    if 'recommend' in qry.lower():
        risk = request.args.get('risk', user_profile['risk_preference']).lower()
        if risk not in RISK_LEVELS:
            return jsonify({'error': f"Invalid risk: choose {list(RISK_LEVELS.keys())}"}), 400
        return jsonify(get_recommendations(amt, risk))

    ticker = raw_t.upper() if raw_t.upper() in SUPPORTED_TICKERS else None
    if not ticker and qry:
        _, ticker = extract_company_and_ticker(qry)
    if not ticker:
        return jsonify({
            'error':'Could not identify stock',
            'suggestions':['?ticker=AAPL','?query="recommend" to get portfolio']
        }), 400

    result = perform_analysis(ticker, amt)
    return jsonify(result), (200 if 'error' not in result else 500)

@app.route('/api/recommend', methods=['GET'])
def recommend_endpoint():
    amt  = float(request.args.get('amount', user_profile['available_amount']))
    risk = request.args.get('risk', user_profile['risk_preference']).lower()
    if risk not in RISK_LEVELS:
        return jsonify({'error': f"Invalid risk: choose {list(RISK_LEVELS.keys())}"}), 400
    return jsonify(get_recommendations(amt, risk))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
