
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


import os
import requests
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, jsonify, request
from flask_cors import CORS
import nltk
import logging
from dotenv import load_dotenv
import yfinance as yf

# Initialize
load_dotenv()
nltk.download('vader_lexicon')
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Configuration
SUPPORTED_TICKERS = [
    'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS',
    'KO', 'PEP', 'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME',
    'TSLA', 'F', 'COIN', 'MRNA'
]

COMPANY_NAME_TO_TICKER = {
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'nvidia': 'NVDA',
    'amd': 'AMD',
    'johnson & johnson': 'JNJ',
    'jnj': 'JNJ',
    'pfizer': 'PFE',
    'pfe': 'PFE',
    'jpmorgan': 'JPM',
    'jpm': 'JPM',
    'goldman sachs': 'GS',
    'gs': 'GS',
    'coca cola': 'KO',
    'ko': 'KO',
    'pepsi': 'PEP',
    'pep': 'PEP',
    'exxon': 'XOM',
    'xom': 'XOM',
    'next era energy': 'NEE',
    'nee': 'NEE',
    'chevron': 'CVX',
    'cvx': 'CVX',
    'walmart': 'WMT',
    'wmt': 'WMT',
    'home depot': 'HD',
    'hd': 'HD',
    'gamestop': 'GME',
    'gme': 'GME',
    'tesla': 'TSLA',
    'tsla': 'TSLA',
    'ford': 'F',
    'f': 'F',
    'coinbase': 'COIN',
    'coin': 'COIN',
    'moderna': 'MRNA',
    'mrna': 'MRNA'
}

# Load models
finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
roberta = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
vader = SentimentIntensityAnalyzer()
gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")

# Fetch stock-related news with ticker symbol directly for better relevance
def fetch_news(ticker):
    """Fetch stock-related news with ticker symbol directly for better relevance."""
    NEWS_API_KEY = ""  # Your actual key
    
    if not NEWS_API_KEY:
        raise ValueError("NewsAPI key not configured")
    
    # Directly use the stock ticker symbol in the query and broaden the search
    query = f"{ticker} stock news"  # Simplified query
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check if the response is successful
        if data['status'] != 'ok':
            raise ValueError(data.get('message', 'NewsAPI error'))

        # If no articles, log it
        if not data['articles']:
            logging.warning(f"No articles found for ticker {ticker}.")
        
        # Return the fetched articles (with more relevant stock-related titles)
        return [
            (article['title'], article['source']['name'], article['description'], article['url'])
            for article in data['articles']
            if 'stock' in article['title'].lower() or 'earnings' in article['title'].lower()
        ]
    
    except Exception as e:
        logging.error(f"News fetch failed: {str(e)}")
        raise ValueError(f"Could not fetch news: {str(e)}")

# Get stock data using yfinance
def get_stock_data(ticker):
    """Get current stock price using yfinance"""
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    if data.empty:
        return None
    return {
        'current_price': round(data['Close'].iloc[-1], 2),
        'change': round(data['Close'].iloc[-1] - data['Open'].iloc[-1], 2),
        'change_percent': round(((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100, 2)
    }

# Sentiment analysis using multiple models
def analyze_sentiment(text):
    """Fixed-weight ensemble sentiment analysis"""
    # Get predictions
    finbert_result = finbert(text)[0]
    roberta_result = roberta(text)[0]
    vader_score = vader.polarity_scores(text)['compound']
    
    # Convert to common scale (-1 to 1)
    finbert_score = 1 if finbert_result['label'] == 'Positive' else -1 if finbert_result['label'] == 'Negative' else 0
    roberta_score = (roberta_result['score'] if roberta_result['label'] == 'POS' else 
                    -roberta_result['score'] if roberta_result['label'] == 'NEG' else 0)
    
    # Fixed weights (calibrated for stability)
    weighted_score = (0.6 * finbert_score) + (0.3 * roberta_score) + (0.1 * vader_score)
    
    # Classify with hysteresis to reduce fluctuation
    if weighted_score > 0.35: return 'Positive', weighted_score
    if weighted_score < -0.35: return 'Negative', weighted_score
    return 'Neutral', weighted_score

# GPT-2 model powered analysis generation
def generate_analysis(ticker, news_items, overall_sentiment):
    """Generate GPT-2 powered analysis"""
    prompt = f"Analyze {ticker} stock sentiment based on these news headlines:\n"
    prompt += "\n".join([f"- {headline}" for headline, _ in news_items])
    prompt += f"\n\nOverall sentiment is {overall_sentiment}. Provide concise investment advice:"
    
    inputs = gpt2_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = gpt2_model.generate(
        **inputs,
        max_length=200,
        num_return_sequences=1,
        temperature=0.7,
        do_sample=True
    )
    
    return gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

# Endpoint to fetch supported tickers
@app.route('/api/stocks', methods=['GET'])
def get_supported_stocks():
    """List supported tickers"""
    return jsonify({
        "tickers": SUPPORTED_TICKERS,
        "mappings": COMPANY_NAME_TO_TICKER
    })

# Main analysis endpoint
@app.route('/api/analyze', methods=['GET'])
def analyze_stock():
    """Main analysis endpoint"""
    ticker_or_name = request.args.get('stock', '').upper()
    
    # Resolve input to ticker
    ticker = None
    if ticker_or_name in SUPPORTED_TICKERS:
        ticker = ticker_or_name
    elif ticker_or_name.lower() in COMPANY_NAME_TO_TICKER:
        ticker = COMPANY_NAME_TO_TICKER[ticker_or_name.lower()]
    
    if not ticker:
        return jsonify({"error": "Unsupported stock"}), 400
    
    try:
        # Fetch all data
        news_items = fetch_news(ticker)
        stock_data = get_stock_data(ticker)
        
        # Analyze sentiment
        analyzed_news = []
        sentiment_scores = []
        
        for headline, source, description, url in news_items:
            sentiment, score = analyze_sentiment(headline)  # Correct unpacking here
            analyzed_news.append({
                "headline": headline,
                "source": source,
                "sentiment": sentiment,
                "score": round(score, 2),
                "description": description,
                "url": url  # Add URL to the response
            })
            sentiment_scores.append(score)
        
        # Calculate overall
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        overall_sentiment = "Positive" if avg_score > 0.35 else "Negative" if avg_score < -0.35 else "Neutral"
        
        # Generate GPT-2 analysis
        gpt_analysis = generate_analysis(ticker, news_items, overall_sentiment)
        
        return jsonify({
            "ticker": ticker,
            "news": analyzed_news,
            "stock_data": stock_data,
            "overall_sentiment": overall_sentiment,
            "average_score": round(avg_score, 2),
            "analysis": gpt_analysis
        })
        
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
