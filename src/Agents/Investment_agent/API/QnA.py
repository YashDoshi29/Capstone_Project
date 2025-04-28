# import requests
# import json
# import re
# import time

# # --- API Keys ---
# ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'

# # ============================
# # COMPONENTS
# # ============================

# # ✅ Company Name → Ticker Mapping
# COMPANY_TICKERS = {
#     "apple": "AAPL",
#     "microsoft": "MSFT",
#     "tesla": "TSLA",
#     "amazon": "AMZN",
#     "google": "GOOGL",
#     "meta": "META",
#     "nvidia": "NVDA",
#     "netflix": "NFLX"
# }

# class StockDataFetcher:
#     def fetch_global_quote(self, symbol):
#         """ Fetches real-time stock price data. """
#         url = "https://www.alphavantage.co/query"
#         params = {
#             "function": "GLOBAL_QUOTE",
#             "symbol": symbol,
#             "apikey": ALPHA_VANTAGE_API_KEY
#         }

#         # ✅ Handling API Rate Limits
#         for _ in range(3):  # Try 3 times in case of rate limits
#             response = requests.get(url, params=params)
#             if response.status_code == 200:
#                 try:
#                     data = response.json()
#                     print(f"📡 API Response for {symbol}: {json.dumps(data, indent=4)}")  # Debugging API response
#                     return data.get("Global Quote", {})
#                 except json.JSONDecodeError:
#                     print(f"❌ Error decoding API response for {symbol}. Retrying...")
#             else:
#                 print(f"⚠️ API Error {response.status_code}: Retrying...")
#             time.sleep(5)  # Wait before retrying
#         return None  # Return None if API fails after retries


# class QueryProcessor:
#     def extract_stock_symbol(self, query):
#         """ Extracts stock symbol or converts company name to ticker. """
#         query = query.lower()

#         # ✅ 1️⃣ First check if a company name is present in the dictionary
#         for company, ticker in COMPANY_TICKERS.items():
#             if company in query:
#                 print(f"🔍 Recognized company '{company}' as ticker '{ticker}'")  # Debugging
#                 return ticker

#         # ✅ 2️⃣ Check for ticker symbols (Case-Insensitive)
#         ticker_match = re.findall(r'\b[A-Z]{2,5}\b', query, re.IGNORECASE)
#         if ticker_match:
#             symbol = ticker_match[0].upper()  # Take the first match
#             print(f"🔍 Found ticker symbol '{symbol}' in query.")  # Debugging
#             return symbol

#         print(f"⚠️ No valid stock symbol found in query: {query}")  # Debugging
#         return None  # No valid stock symbol found

#     def determine_query_type(self, query):
#         """ Determines the type of user query. """
#         query = query.lower()
#         if "price" in query or "current value" in query:
#             return "price"
#         elif "closing price" in query or "last close" in query:
#             return "closing_price"
#         else:
#             return "unknown"

# # =======================
# # Chatbot Function
# # =======================
# def chatbot():
#     stock_fetcher = StockDataFetcher()
#     query_processor = QueryProcessor()

#     print("\n💬 Welcome to the Financial Chatbot! Type 'exit' to stop.")

#     while True:
#         user_query = input("\nYou: ").strip()
#         if user_query.lower() == "exit":
#             print("\n👋 Goodbye!")
#             break

#         # ✅ Extract stock symbol
#         symbol = query_processor.extract_stock_symbol(user_query)
#         if not symbol:
#             print("🤖 Chatbot: Please mention a valid stock or company name (e.g., 'Apple', 'AAPL').")
#             continue

#         # ✅ Determine query type
#         query_type = query_processor.determine_query_type(user_query)

#         # ✅ Handle Different Query Types
#         if query_type == "price":
#             global_quote = stock_fetcher.fetch_global_quote(symbol)
#             if global_quote and "05. price" in global_quote:
#                 price = global_quote["05. price"]
#                 print(f"🤖 Chatbot: The latest price of {symbol} is **${price}**.")
#             else:
#                 print(f"🤖 Chatbot: Unable to retrieve stock price for {symbol}. Check API response above.")

#         elif query_type == "closing_price":
#             global_quote = stock_fetcher.fetch_global_quote(symbol)
#             if global_quote and "08. previous close" in global_quote:
#                 closing_price = global_quote["08. previous close"]
#                 print(f"🤖 Chatbot: The last closing price of {symbol} was **${closing_price}**.")
#             else:
#                 print(f"🤖 Chatbot: Unable to retrieve closing price for {symbol}. Check API response above.")

#         else:
#             print("🤖 Chatbot: I can fetch stock prices and closing prices. Try asking about stock trends or valuations!")

# if __name__ == "__main__":
#     chatbot()



import requests
import json
import re
import time
from datetime import datetime, timedelta

# --- API Keys ---
ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'

# ============================
# COMPONENTS
# ============================

# ✅ Company Name → Ticker Mapping
COMPANY_TICKERS = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "tesla": "TSLA",
    "amazon": "AMZN",
    "google": "GOOGL",
    "meta": "META",
    "nvidia": "NVDA",
    "netflix": "NFLX"
}

class StockDataFetcher:
    def fetch_global_quote(self, symbol):
        """ Fetches real-time stock price data. """
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(url, params=params)
        try:
            data = response.json()
            if "Global Quote" in data and data["Global Quote"]:
                print(f"📡 API Response for {symbol}: {json.dumps(data, indent=4)}")  # Debugging API response
                return data["Global Quote"]
            else:
                print(f"❌ API Error: No data found for {symbol} - Response: {data}")
                return None
        except json.JSONDecodeError:
            print("❌ Error decoding API response for", symbol)
            return None

    def fetch_historical_data(self, symbol):
        """ Fetches historical stock price data for trend analysis. """
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(url, params=params)
        try:
            data = response.json()
            return data.get("Time Series (Daily)", {})
        except json.JSONDecodeError:
            print("❌ Error decoding API response for", symbol)
            return {}

class QueryProcessor:
    def extract_stock_symbol(self, query):
        """ Extracts stock symbol or converts company name to ticker. """
        query = query.lower()

        # ✅ 1️⃣ Check if a company name is present in the dictionary
        for company, ticker in COMPANY_TICKERS.items():
            if company in query:
                print(f"🔍 Recognized company '{company}' as ticker '{ticker}'")  # Debugging
                return ticker

        # ✅ 2️⃣ Check for ticker symbols (Case-Insensitive)
        ticker_match = re.findall(r'\b[A-Z]{2,5}\b', query, re.IGNORECASE)
        if ticker_match:
            symbol = ticker_match[0].upper()  # Take the first match
            print(f"🔍 Found ticker symbol '{symbol}' in query.")  # Debugging
            return symbol

        print(f"⚠️ No valid stock symbol found in query: {query}")  # Debugging
        return None  # No valid stock symbol found

    def determine_query_type(self, query):
        """ Determines the type of user query. """
        query = query.lower()
        if "open price" in query:
            return "open_price"
        elif "closing price" in query or "last close" in query or "yesterday" in query:
            return "closing_price"
        elif "high price" in query or "highest price" in query:
            return "high_price"
        elif "low price" in query or "lowest price" in query:
            return "low_price"
        elif "trend" in query or "past few days" in query:
            return "trend"
        elif "stock data" in query or "all details" in query or "tell me about" in query:
            return "full_data"
        else:
            return "unknown"

# =======================
# Chatbot Function
# =======================
def chatbot():
    stock_fetcher = StockDataFetcher()
    query_processor = QueryProcessor()

    print("\n💬 Welcome to the Financial Chatbot! Type 'exit' to stop.")

    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() == "exit":
            print("\n👋 Goodbye!")
            break

        # ✅ Extract stock symbol
        symbol = query_processor.extract_stock_symbol(user_query)
        if not symbol:
            print("🤖 Chatbot: Please mention a valid stock or company name (e.g., 'Apple', 'AAPL').")
            continue

        # ✅ Determine query type
        query_type = query_processor.determine_query_type(user_query)

        # ✅ Fetch real-time stock data
        global_quote = stock_fetcher.fetch_global_quote(symbol)
        if not global_quote:
            print(f"🤖 Chatbot: Unable to retrieve stock data for {symbol}. Please try again later.")
            continue

        # ✅ Fetch historical stock data if needed
        historical_data = None
        if query_type == "trend":
            historical_data = stock_fetcher.fetch_historical_data(symbol)

        # ✅ Handle Different Query Types
        if query_type == "open_price":
            open_price = global_quote.get("02. open", "N/A")
            print(f"🤖 Chatbot: The opening price of {symbol} today was **${open_price}**.")

        elif query_type == "closing_price":
            closing_price = global_quote.get("08. previous close", "N/A")
            print(f"🤖 Chatbot: The last closing price of {symbol} was **${closing_price}**.")

        elif query_type == "high_price":
            high_price = global_quote.get("03. high", "N/A")
            print(f"🤖 Chatbot: The highest price of {symbol} today was **${high_price}**.")

        elif query_type == "low_price":
            low_price = global_quote.get("04. low", "N/A")
            print(f"🤖 Chatbot: The lowest price of {symbol} today was **${low_price}**.")

        elif query_type == "trend":
            if not historical_data:
                print(f"🤖 Chatbot: Unable to retrieve historical data for {symbol}.")
            else:
                last_five_days = list(historical_data.keys())[:5]  # Get the last 5 trading days
                trend_info = "\n".join(
                    [f"{date}: ${historical_data[date]['4. close']}" for date in last_five_days]
                )
                print(f"🤖 Chatbot: The trend for {symbol} over the last 5 days:\n{trend_info}")

        elif query_type == "full_data":
            open_price = global_quote.get("02. open", "N/A")
            high_price = global_quote.get("03. high", "N/A")
            low_price = global_quote.get("04. low", "N/A")
            price = global_quote.get("05. price", "N/A")
            volume = global_quote.get("06. volume", "N/A")
            closing_price = global_quote.get("08. previous close", "N/A")
            print(f"🤖 Chatbot: Here’s the latest stock data for {symbol}:\n"
                  f"🔹 Open: **${open_price}**\n"
                  f"🔹 High: **${high_price}**\n"
                  f"🔹 Low: **${low_price}**\n"
                  f"🔹 Current Price: **${price}**\n"
                  f"🔹 Previous Close: **${closing_price}**\n"
                  f"🔹 Volume: **{volume}**")

        else:
            print("🤖 Chatbot: Try asking about open price, high price, stock trends, or full stock data!")

if __name__ == "__main__":
    chatbot()
