# from flask import Flask, request, jsonify
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import datetime

# app = Flask(__name__)

# # Load the fine-tuned FinBERT model and tokenizer from your saved directory.
# model_path = "/Users/nemi/finetuned_finbert"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForSequenceClassification.from_pretrained(model_path)
# # Create a classification pipeline.
# classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, framework="pt")

# def get_stock_indicators(ticker):
#     """
#     Simulated function to fetch current technical indicator values.
#     In production, you would replace this with a function that fetches real-time data,
#     computes indicators (e.g., SMA, EMA, RSI, MACD, OBV, ATR), and returns them in a dict.
#     """
#     now = datetime.datetime.now()
#     date_str = now.strftime("%Y-%m-%d")
#     # Simulated indicator values (replace with actual retrieval/calculation)
#     return {
#         "ticker": ticker,
#         "Date": date_str,
#         "Close": 150.00,
#         "SMA20": 148.50,
#         "EMA20": 149.00,
#         "RSI14": 55.00,
#         "MACD": 0.50,
#         "OBV": 10000000,
#         "ATR14": 1.20
#     }

# def format_prompt(indicators):
#     """
#     Formats the technical indicator values into a prompt string that mirrors the training prompt.
#     """
#     return (
#         f"Stock: {indicators['ticker']}, Date: {indicators['Date']}, "
#         f"Close: {indicators['Close']:.2f}, SMA20: {indicators['SMA20']:.2f}, EMA20: {indicators['EMA20']:.2f}, "
#         f"RSI14: {indicators['RSI14']:.2f}, MACD: {indicators['MACD']:.2f}, OBV: {indicators['OBV']:.0f}, "
#         f"ATR14: {indicators['ATR14']:.2f}. Predict if tomorrow's price will go Up or Down:"
#     )

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     if 'ticker' not in data:
#         return jsonify({"error": "Ticker symbol not provided"}), 400

#     ticker = data['ticker']
#     # Fetch current technical indicators (or simulated values).
#     indicators = get_stock_indicators(ticker)
#     # Create a prompt string based on those indicators.
#     prompt = format_prompt(indicators)
    
#     # Use the classifier pipeline to predict the outcome.
#     result = classifier(prompt)
#     # The pipeline returns a list with a dictionary containing 'label' and 'score'
#     predicted_label = result[0]['label']
#     confidence = result[0]['score']
#     # Map the returned label to "Up" or "Down" (assuming LABEL_1 corresponds to "Up")
#     prediction = "Up" if predicted_label.endswith("1") else "Down"
    
#     # Return the prediction along with the confidence and other details.
#     return jsonify({
#         "ticker": ticker,
#         "date": indicators["Date"],
#         "prediction": prediction,
#         "confidence": confidence,
#         "raw_result": result
#     })

# if __name__ == '__main__':
#     # Run the Flask app on port 5000.
#     app.run(host="0.0.0.0", port=5050, debug=True)



# from flask import Flask, request, jsonify
# import yfinance as yf
# import pandas as pd
# import ta
# import datetime
# import numpy as np
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM, pipeline

# app = Flask(__name__)

# # ----- Model and Pipeline Setup -----
# finbert_model_path = "/Users/nemi/finetuned_finbert"  # adjust this path if needed
# finbert_tokenizer = AutoTokenizer.from_pretrained(finbert_model_path)
# finbert_model = AutoModelForSequenceClassification.from_pretrained(finbert_model_path)
# finbert_classifier = pipeline("text-classification", model=finbert_model, tokenizer=finbert_tokenizer, framework="pt")

# gpt_model_name = "EleutherAI/gpt-neo-1.3B"  # or another generative model
# gpt_tokenizer = AutoTokenizer.from_pretrained(gpt_model_name)
# gpt_model = AutoModelForCausalLM.from_pretrained(gpt_model_name)
# gpt_generator = pipeline("text-generation", model=gpt_model, tokenizer=gpt_tokenizer, framework="pt", max_length=500)

# # ----- Company Lookup for Query Parsing -----
# company_lookup = {
#     "aapl": {"company_name": "Apple Inc.", "ticker": "AAPL"},
#     "jnj": {"company_name": "Johnson & Johnson", "ticker": "JNJ"},
#     "f": {"company_name": "Ford Motor Company", "ticker": "F"},
#     "pep": {"company_name": "PepsiCo Inc.", "ticker": "PEP"},
#     "gme": {"company_name": "GameStop Corp.", "ticker": "GME"}
#     # Add more as needed.
# }

# def parse_query(query):
#     query_lower = query.lower()
#     for key, details in company_lookup.items():
#         if key in query_lower:
#             standardized_query = f"Shall I invest in {details['company_name']} right now?"
#             return standardized_query, details["company_name"], details["ticker"]
#     return query, "Unknown Company", "UNKNOWN"

# # ----- Data Retrieval and Indicator Computation -----
# def fetch_real_time_data(ticker, min_rows=20, initial_days=180, max_days=365):
#     """
#     Fetches daily data for the given ticker until at least `min_rows` rows are returned.
#     Uses auto_adjust=True for consistency.
#     Resets the index and flattens columns if they are a MultiIndex, then forces all column names to Title case.
#     """
#     days = initial_days
#     while days <= max_days:
#         end_date = datetime.datetime.now().date()
#         start_date = end_date - datetime.timedelta(days=days)
#         print(f"Fetching data for {ticker} from {start_date} to {end_date} (window: {days} days)")
#         df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
#         if df is None or df.empty:
#             print(f"No data returned for {ticker} in a {days}-day window.")
#         else:
#             print(f"Fetched {len(df)} rows for {ticker}")
#             if len(df) >= min_rows:
#                 df.reset_index(inplace=True)
#                 # If columns are a MultiIndex, flatten them.
#                 if isinstance(df.columns, pd.MultiIndex):
#                     df.columns = df.columns.get_level_values(0)
#                 else:
#                     df.columns = [col.strip().title() if isinstance(col, str) else col for col in df.columns]
#                 # Ensure a "Date" column exists.
#                 if "Date" not in df.columns:
#                     df["Date"] = df.index
#                 # Ensure required columns are present.
#                 required_cols = ["Close", "High", "Low", "Volume"]
#                 missing_cols = [col for col in required_cols if col not in df.columns]
#                 if missing_cols:
#                     print("Missing required columns:", missing_cols)
#                     return None
#                 return df
#         days += 30
#     print(f"Could not fetch at least {min_rows} rows for {ticker} within {max_days} days.")
#     return None


# def compute_indicators_from_df(df):
#     """
#     Computes technical indicators using the ta library and returns the latest row as a dictionary.
#     Also adds the date from the DataFrame's "Date" column as a Python datetime object.
#     """
#     if len(df) < 20:
#         return None
#     df = df.copy()
#     if "Date" not in df.columns:
#         df["Date"] = df.index
#     df.sort_values("Date", inplace=True)
    
#     required_cols = ["Close", "High", "Low", "Volume"]
#     if not all(col in df.columns for col in required_cols):
#         print("Missing required columns:", [col for col in required_cols if col not in df.columns])
#         return None
    
#     close_series = df["Close"].squeeze()
#     high_series = df["High"].squeeze()
#     low_series = df["Low"].squeeze()
#     volume_series = df["Volume"].squeeze()
    
#     df["SMA20"] = close_series.rolling(window=20).mean()
#     df["EMA20"] = close_series.ewm(span=20, adjust=False).mean()
#     df["RSI14"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    
#     macd_obj = ta.trend.MACD(close=close_series)
#     df["MACD"] = macd_obj.macd()
#     df["MACD_signal"] = macd_obj.macd_signal()
#     df["MACD_diff"] = macd_obj.macd_diff()
    
#     df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=close_series, volume=volume_series).on_balance_volume()
#     df["ATR14"] = ta.volatility.AverageTrueRange(high=high_series, low=low_series, close=close_series, window=14).average_true_range()
    
#     latest = df.iloc[-1].to_dict()
#     latest["Date"] = pd.to_datetime(df.iloc[-1]["Date"]).to_pydatetime()
#     return latest

# def format_prompt(indicators, ticker):
#     """
#     Formats a prompt string using the computed technical indicators.
#     Expects 'indicators' to be a dictionary with a scalar 'Date' value.
#     """
#     date_value = indicators["Date"]
#     try:
#         date_str = date_value.strftime("%Y-%m-%d")
#     except Exception:
#         date_str = str(date_value)
    
#     prompt = (
#         f"Stock: {ticker}, Date: {date_str}, "
#         f"Close: {indicators['Close']:.2f}, SMA20: {indicators['SMA20']:.2f}, EMA20: {indicators['EMA20']:.2f}, "
#         f"RSI14: {indicators['RSI14']:.2f}, MACD: {indicators['MACD']:.2f}, OBV: {indicators['OBV']:.0f}, "
#         f"ATR14: {indicators['ATR14']:.2f}. Predict if tomorrow's price will go Up or Down:"
#     )
#     return prompt

# # ----- Root Route (Optional) -----
# @app.route("/")
# def index():
#     return "Welcome to the Financial Advisor API! Use /analyze_stock endpoint for predictions."

# # ----- API Endpoint -----
# @app.route('/analyze_stock', methods=['POST'])
# def analyze_stock():
#     data = request.get_json()
#     if "query" not in data:
#         return jsonify({"error": "Query is required."}), 400

#     user_query = data["query"]
#     standardized_query, company_name, ticker = parse_query(user_query)
    
#     if ticker == "UNKNOWN":
#         return jsonify({"error": f"Could not determine company for query: {user_query}"}), 400
    
#     df = fetch_real_time_data(ticker)
#     if df is None or df.empty:
#         return jsonify({"error": f"Could not fetch data for ticker {ticker}."}), 400
    
#     indicators = compute_indicators_from_df(df)
#     if indicators is None:
#         return jsonify({"error": "Not enough data to compute technical indicators."}), 400
    
#     prompt = format_prompt(indicators, ticker)
#     result = finbert_classifier(prompt)
#     predicted_label = result[0]["label"]
#     confidence = result[0]["score"]
#     prediction = "Up" if predicted_label.endswith("1") else "Down"
    
#     analysis_prompt = (
#         f"Analyze the stock {company_name} with ticker {ticker}.\n"
#         f"User Query: {standardized_query}\n"
#         f"Technical Data: {prompt}\n"
#         f"FinBERT Prediction: {prediction} with confidence {confidence:.2f}.\n"
#         f"Generate an investment thesis covering financial performance, market trends, risks, and outlook."
#     )
#     analysis_output = gpt_generator(analysis_prompt, max_length=500)[0]["generated_text"]
    
#     response = {
#         "Query": standardized_query,
#         "Company_name": company_name,
#         "Ticker": ticker,
#         "Prediction": prediction,
#         "Confidence": confidence,
#         "Analysis": analysis_output
#     }
#     return jsonify(response)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5050, debug=True)


# from flask import Flask, request, jsonify
# import yfinance as yf
# import pandas as pd
# import ta
# import datetime
# import numpy as np
# from transformers import (
#     AutoTokenizer,
#     AutoModelForSequenceClassification,
#     AutoModelForCausalLM,
#     pipeline
# )
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # ----- Model and Pipeline Setup -----
# # Load the fine-tuned FinBERT model (for stock movement prediction).
# finbert_model_path = "/Users/nemi/finetuned_finbert"  # Path to your saved FinBERT model
# finbert_tokenizer = AutoTokenizer.from_pretrained(finbert_model_path)
# finbert_model = AutoModelForSequenceClassification.from_pretrained(finbert_model_path)
# finbert_classifier = pipeline("text-classification", model=finbert_model, tokenizer=finbert_tokenizer, framework="pt")

# # Load a generative model (GPT-Neo or GPT-J) for generating detailed investment analysis.
# gpt_model_name = "EleutherAI/gpt-neo-1.3B"  # Change to GPT-J if preferred
# gpt_tokenizer = AutoTokenizer.from_pretrained(gpt_model_name)
# gpt_model = AutoModelForCausalLM.from_pretrained(gpt_model_name)
# gpt_generator = pipeline("text-generation", model=gpt_model, tokenizer=gpt_tokenizer, framework="pt", max_length=500, truncation=True)

# # ----- Company Lookup for Query Parsing -----
# company_lookup = {
#     "aapl": {"company_name": "Apple Inc.", "ticker": "AAPL"},
#     "jnj": {"company_name": "Johnson & Johnson", "ticker": "JNJ"},
#     "f": {"company_name": "Ford Motor Company", "ticker": "F"},
#     "pep": {"company_name": "PepsiCo Inc.", "ticker": "PEP"},
#     "gme": {"company_name": "GameStop Corp.", "ticker": "GME"}
#     # Add additional mappings as needed.
# }

# def parse_query(query: str):
#     """
#     Extracts a standardized query, company name, and ticker from the user query.
#     """
#     query_lower = query.lower()
#     for key, details in company_lookup.items():
#         if key in query_lower:
#             standardized_query = f"Shall I invest in {details['company_name']} right now?"
#             return standardized_query, details["company_name"], details["ticker"]
#     return query, "Unknown Company", "UNKNOWN"

# # ----- Data Retrieval and Indicator Computation -----
# def fetch_real_time_data(ticker: str, min_rows: int = 20, initial_days: int = 180, max_days: int = 365):
#     """
#     Fetches recent daily data for the given ticker using yfinance until at least `min_rows` rows are returned.
#     Uses auto_adjust=True for consistency. Resets the index and forces column names to Title case.
#     """
#     days = initial_days
#     while days <= max_days:
#         end_date = datetime.datetime.now().date()
#         start_date = end_date - datetime.timedelta(days=days)
#         logger.info(f"Fetching data for {ticker} from {start_date} to {end_date} (window: {days} days)")
#         df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
#         if df is None or df.empty:
#             logger.warning(f"No data returned for {ticker} in a {days}-day window.")
#         else:
#             logger.info(f"Fetched {len(df)} rows for {ticker}")
#             if len(df) >= min_rows:
#                 df.reset_index(inplace=True)
#                 # Flatten MultiIndex if present, and force Title case on column names.
#                 if isinstance(df.columns, pd.MultiIndex):
#                     df.columns = df.columns.get_level_values(0)
#                 else:
#                     df.columns = [col.strip().title() if isinstance(col, str) else col for col in df.columns]
#                 # Ensure "Date" column exists.
#                 if "Date" not in df.columns:
#                     df["Date"] = df.index
#                 # Check for required columns.
#                 required_cols = ["Close", "High", "Low", "Volume"]
#                 missing = [col for col in required_cols if col not in df.columns]
#                 if missing:
#                     logger.warning(f"Missing required columns for {ticker}: {missing}")
#                     return None
#                 return df
#         days += 30
#     logger.error(f"Could not fetch at least {min_rows} rows for {ticker} within {max_days} days.")
#     return None

# def compute_indicators_from_df(df: pd.DataFrame):
#     """
#     Computes technical indicators using the ta library and returns the latest row as a dictionary.
#     Also, explicitly adds the date from the DataFrame's "Date" column as a Python datetime.
#     """
#     if len(df) < 20:
#         return None
#     df = df.copy()
#     if "Date" not in df.columns:
#         df["Date"] = df.index
#     df.sort_values("Date", inplace=True)
#     required_cols = ["Close", "High", "Low", "Volume"]
#     if not all(col in df.columns for col in required_cols):
#         logger.error("Missing required columns in DataFrame.")
#         return None
#     close_series = df["Close"].squeeze()
#     high_series = df["High"].squeeze()
#     low_series = df["Low"].squeeze()
#     volume_series = df["Volume"].squeeze()
    
#     df["SMA20"] = close_series.rolling(window=20).mean()
#     df["EMA20"] = close_series.ewm(span=20, adjust=False).mean()
#     df["RSI14"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    
#     macd_obj = ta.trend.MACD(close=close_series)
#     df["MACD"] = macd_obj.macd()
#     df["MACD_signal"] = macd_obj.macd_signal()
#     df["MACD_diff"] = macd_obj.macd_diff()
    
#     df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=close_series, volume=volume_series).on_balance_volume()
#     df["ATR14"] = ta.volatility.AverageTrueRange(high=high_series, low=low_series, close=close_series, window=14).average_true_range()
    
#     latest = df.iloc[-1].to_dict()
#     latest["Date"] = pd.to_datetime(df.iloc[-1]["Date"]).to_pydatetime()
#     return latest

# def format_prompt(indicators: dict, ticker: str):
#     """
#     Formats a prompt string using the computed technical indicators.
#     Expects 'indicators' to be a dictionary with a scalar 'Date' value.
#     """
#     date_value = indicators["Date"]
#     try:
#         date_str = date_value.strftime("%Y-%m-%d")
#     except Exception:
#         date_str = str(date_value)
    
#     prompt = (
#         f"Stock: {ticker}, Date: {date_str}, "
#         f"Close: {indicators['Close']:.2f}, SMA20: {indicators['SMA20']:.2f}, EMA20: {indicators['EMA20']:.2f}, "
#         f"RSI14: {indicators['RSI14']:.2f}, MACD: {indicators['MACD']:.2f}, OBV: {indicators['OBV']:.0f}, "
#         f"ATR14: {indicators['ATR14']:.2f}. Predict if tomorrow's price will go Up or Down:"
#     )
#     return prompt

# # ----- API Endpoint for Financial Advice -----
# @app.route('/api/financial-advice', methods=['POST'])
# def financial_advice():
#     """
#     Expects a JSON payload with:
#       - query: A natural language query about investing in a stock.
#       - budget: (Optional) A numerical value representing the remaining budget.
#     Returns a JSON response with the standardized query, company info, predicted stock movement,
#     and a detailed investment thesis including suggestions for allocation.
#     """
#     data = request.get_json()
#     if "query" not in data:
#         return jsonify({"error": "Query is required."}), 400

#     user_query = data["query"]
#     budget = data.get("budget")  # budget is optional
#     standardized_query, company_name, ticker = parse_query(user_query)
    
#     if ticker == "UNKNOWN":
#         return jsonify({"error": f"Could not determine company for query: {user_query}"}), 400

#     df = fetch_real_time_data(ticker)
#     if df is None or df.empty:
#         return jsonify({"error": f"Could not fetch data for ticker {ticker}."}), 400

#     indicators = compute_indicators_from_df(df)
#     if indicators is None:
#         return jsonify({"error": "Not enough data to compute technical indicators."}), 400

#     prompt = format_prompt(indicators, ticker)
#     logger.info("FinBERT prompt: %s", prompt)
#     result = finbert_classifier(prompt)
#     predicted_label = result[0]["label"]
#     confidence = result[0]["score"]
#     prediction = "Up" if predicted_label.endswith("1") else "Down"

#     # Build the analysis prompt. If a budget is provided, include it.
#     analysis_prompt = (
#     f"Analyze the stock {company_name} with ticker {ticker}.\n"
#     f"User Query: {standardized_query}\n"
#     f"Technical Data: {prompt}\n"
#     f"FinBERT Prediction: {prediction} with confidence {confidence:.2f}.\n"
#     f"Remaining investment budget: ${budget:.2f}.\n"
#     f"Based on this information, provide a detailed investment thesis that includes:\n"
#     f"1. A summary of the current financial and market conditions for {company_name}.\n"
#     f"2. A specific recommendation on how much to invest in {company_name} from the ${budget:.2f} budget (e.g., invest $X in {ticker}).\n"
#     f"3. If applicable, suggestions for diversifying the remaining budget among other stocks.\n"
#     f"Please output your answer in a clear, bullet-point format with a conclusion."
#     )

#     if budget:
#         analysis_prompt += f"Remaining investment budget: ${budget:.2f}.\n"
#     analysis_prompt += (
#         "Generate an investment thesis covering financial performance, market trends, risks, outlook, "
#         "and suggest how to allocate the budget across this stock (or with diversification recommendations)."
#     )
#     logger.info("GPT analysis prompt: %s", analysis_prompt)
#     analysis_output = gpt_generator(analysis_prompt, max_length=500, truncation=True)[0]["generated_text"]
#     logger.info("GPT output: %s", analysis_output)

#     response = {
#         "Query": standardized_query,
#         "Company_name": company_name,
#         "Ticker": ticker,
#         "Prediction": prediction,
#         "Confidence": confidence,
#         "Analysis": analysis_output
#     }
#     return jsonify(response)

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "tickers": list(company_lookup.keys())})

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5050, debug=False)


from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import ta
import datetime
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    pipeline
)
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ----- Model and Pipeline Setup -----
finbert_model_path = "/Users/nemi/finetuned_finbert"  # Adjust this path as needed
finbert_tokenizer = AutoTokenizer.from_pretrained(finbert_model_path)
finbert_model = AutoModelForSequenceClassification.from_pretrained(finbert_model_path)
finbert_classifier = pipeline("text-classification", model=finbert_model, tokenizer=finbert_tokenizer, framework="pt")

gpt_model_name = "EleutherAI/gpt-neo-1.3B"  # Change to GPT-J if preferred
gpt_tokenizer = AutoTokenizer.from_pretrained(gpt_model_name)
gpt_model = AutoModelForCausalLM.from_pretrained(gpt_model_name)
gpt_generator = pipeline("text-generation", model=gpt_model, tokenizer=gpt_tokenizer, framework="pt", truncation=True)

# ----- Company Lookup for Query Parsing -----
company_lookup = {
    "aapl": {"company_name": "Apple Inc.", "ticker": "AAPL"},
    "jnj": {"company_name": "Johnson & Johnson", "ticker": "JNJ"},
    "f": {"company_name": "Ford Motor Company", "ticker": "F"},
    "pep": {"company_name": "PepsiCo Inc.", "ticker": "PEP"},
    "gme": {"company_name": "GameStop Corp.", "ticker": "GME"}
    # Add additional companies as needed.
}

def parse_query(query: str):
    query_lower = query.lower()
    for key, details in company_lookup.items():
        if key in query_lower:
            standardized_query = f"Shall I invest in {details['company_name']} right now?"
            return standardized_query, details["company_name"], details["ticker"]
    return query, "Unknown Company", "UNKNOWN"

# ----- News Retrieval (Simulated) -----
def get_recent_news(company_name: str) -> str:
    """
    Simulates retrieval of recent news headlines for a company.
    Replace this with a call to a real news API if needed.
    """
    return (
        f"Headline 1: {company_name} reports strong quarterly earnings.\n"
        f"Headline 2: Analysts remain bullish on {company_name} due to solid fundamentals.\n"
        f"Headline 3: Recent market trends favor growth in the {company_name} sector."
    )

# ----- Data Retrieval and Indicator Computation -----
def fetch_real_time_data(ticker: str, min_rows: int = 20, initial_days: int = 180, max_days: int = 365):
    """
    Fetches recent daily data for the given ticker using yfinance until at least `min_rows` rows are returned.
    Uses auto_adjust=True for consistency. Resets the index and forces all column names to Title case.
    """
    days = initial_days
    while days <= max_days:
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=days)
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date} (window: {days} days)")
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df is None or df.empty:
            logger.warning(f"No data returned for {ticker} in a {days}-day window.")
        else:
            logger.info(f"Fetched {len(df)} rows for {ticker}")
            if len(df) >= min_rows:
                df.reset_index(inplace=True)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                else:
                    df.columns = [col.strip().title() if isinstance(col, str) else col for col in df.columns]
                if "Date" not in df.columns:
                    df["Date"] = df.index
                required_cols = ["Close", "High", "Low", "Volume"]
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    logger.warning(f"Missing required columns for {ticker}: {missing}")
                    return None
                return df
        days += 30
    logger.error(f"Could not fetch at least {min_rows} rows for {ticker} within {max_days} days.")
    return None

def compute_indicators_from_df(df: pd.DataFrame):
    """
    Computes technical indicators using the ta library and returns the latest row as a dictionary.
    Also adds the date from the DataFrame's "Date" column as a Python datetime.
    """
    if len(df) < 20:
        return None
    df = df.copy()
    if "Date" not in df.columns:
        df["Date"] = df.index
    df.sort_values("Date", inplace=True)
    required_cols = ["Close", "High", "Low", "Volume"]
    if not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns in DataFrame.")
        return None
    close_series = df["Close"].squeeze()
    high_series = df["High"].squeeze()
    low_series = df["Low"].squeeze()
    volume_series = df["Volume"].squeeze()
    
    df["SMA20"] = close_series.rolling(window=20).mean()
    df["EMA20"] = close_series.ewm(span=20, adjust=False).mean()
    df["RSI14"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    
    macd_obj = ta.trend.MACD(close=close_series)
    df["MACD"] = macd_obj.macd()
    df["MACD_signal"] = macd_obj.macd_signal()
    df["MACD_diff"] = macd_obj.macd_diff()
    
    df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=close_series, volume=volume_series).on_balance_volume()
    df["ATR14"] = ta.volatility.AverageTrueRange(high=high_series, low=low_series, close=close_series, window=14).average_true_range()
    
    latest = df.iloc[-1].to_dict()
    latest["Date"] = pd.to_datetime(df.iloc[-1]["Date"]).to_pydatetime()
    return latest

def format_prompt(indicators: dict, ticker: str):
    """
    Formats a prompt string using the computed technical indicators.
    Expects 'indicators' to be a dictionary with a scalar 'Date' value.
    """
    date_value = indicators["Date"]
    try:
        date_str = date_value.strftime("%Y-%m-%d")
    except Exception:
        date_str = str(date_value)
    
    prompt = (
        f"Stock: {ticker}, Date: {date_str}, "
        f"Close: {indicators['Close']:.2f}, SMA20: {indicators['SMA20']:.2f}, EMA20: {indicators['EMA20']:.2f}, "
        f"RSI14: {indicators['RSI14']:.2f}, MACD: {indicators['MACD']:.2f}, OBV: {indicators['OBV']:.0f}, "
        f"ATR14: {indicators['ATR14']:.2f}. Predict if tomorrow's price will go Up or Down:"
    )
    return prompt

# ----- API Endpoints -----
@app.route("/")
def index():
    return "Welcome to the Financial Advisor API! Use the /analyze_stock endpoint for predictions."

@app.route('/analyze_stock', methods=['POST'])
def analyze_stock():
    data = request.get_json()
    if "query" not in data:
        return jsonify({"error": "Query is required."}), 400

    user_query = data["query"]
    budget = data.get("budget")  # budget is optional
    standardized_query, company_name, ticker = parse_query(user_query)
    
    if ticker == "UNKNOWN":
        return jsonify({"error": f"Could not determine company for query: {user_query}"}), 400

    df = fetch_real_time_data(ticker)
    if df is None or df.empty:
        return jsonify({"error": f"Could not fetch data for ticker {ticker}."}), 400

    indicators = compute_indicators_from_df(df)
    if indicators is None:
        return jsonify({"error": "Not enough data to compute technical indicators."}), 400

    prompt = format_prompt(indicators, ticker)
    logger.info("FinBERT prompt: %s", prompt)
    result = finbert_classifier(prompt)
    predicted_label = result[0]["label"]
    confidence = result[0]["score"]
    prediction = "Up" if predicted_label.endswith("1") else "Down"

    news_summary = get_recent_news(company_name)
    
    analysis_prompt = (
        f"Analyze the stock {company_name} with ticker {ticker}.\n"
        f"User Query: {standardized_query}\n"
        f"Technical Data: {prompt}\n"
        f"FinBERT Prediction: {prediction} with confidence {confidence:.2f}.\n"
        f"Recent News:\n{news_summary}\n"
    )
    if budget is not None:
        try:
            analysis_prompt += f"Remaining investment budget: ${float(budget):.2f}.\n"
        except Exception:
            analysis_prompt += f"Remaining investment budget: {budget}.\n"
    analysis_prompt += (
        "Based on this information, provide a detailed investment thesis that includes:\n"
        "1. A summary of the current financial and market conditions for the company.\n"
        "2. A clear recommendation on how much to invest in this stock from the given budget.\n"
        "3. If applicable, suggestions for diversifying the remaining budget among other stocks.\n"
        "Please output your answer in bullet points followed by a final conclusion."
    )
    logger.info("GPT analysis prompt: %s", analysis_prompt)
    analysis_output = gpt_generator(analysis_prompt, max_new_tokens=200, truncation=True)[0]["generated_text"]
    logger.info("GPT output: %s", analysis_output)

    response = {
        "Query": standardized_query,
        "Company_name": company_name,
        "Ticker": ticker,
        "Prediction": prediction,
        "Confidence": confidence,
        "Analysis": analysis_output
    }
    return jsonify(response)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "tickers": list(company_lookup.keys())})

if __name__ == '__main__':
    # Run on port 5050 so that curl calls to 5050 will work.
    app.run(host="0.0.0.0", port=5050, debug=False)
