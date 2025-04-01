# from flask import Flask, jsonify, request
# import json
# import requests
# from rapidfuzz import process, fuzz

# # --- API Keys ---
# ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'  # Alpha Vantage API Key

# # ============================
# # COMPONENTS
# # ============================

# class DataCollectionComponent:
#     def fetch_stock_data(self, symbol):
#         """
#         Fetches stock data for a given ticker symbol from Alpha Vantage API.
#         """
#         url = 'https://www.alphavantage.co/query'
#         params = {
#             'function': 'GLOBAL_QUOTE',
#             'symbol': symbol,
#             'apikey': ALPHA_VANTAGE_API_KEY
#         }
#         response = requests.get(url, params=params)

#         # Debugging: print the entire response to see the returned data
#         print(f"API Response for {symbol}: {response.status_code}")
#         print(response.json())  # Print the full response

#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"Error fetching stock data for {symbol}: {response.status_code}")
#             return None

#     def preprocess_stock_data(self, stock_data):
#         """
#         Processes the fetched stock data to extract meaningful information.
#         """
#         if not stock_data:
#             return []
#         quote_data = stock_data.get('Global Quote', {})  # Corrected key from the response
#         if not quote_data:
#             print("No stock data found.")
#             return []
#         document = (
#             f"Stock Data_Synthesizer - Symbol: {quote_data.get('01. symbol', 'N/A')}, "
#             f"Open: {quote_data.get('02. open', 'N/A')}, "
#             f"High: {quote_data.get('03. high', 'N/A')}, "
#             f"Low: {quote_data.get('04. low', 'N/A')}, "
#             f"Price: {quote_data.get('05. price', 'N/A')}, "
#             f"Volume: {quote_data.get('06. volume', 'N/A')}, "
#             f"Latest Trading Day: {quote_data.get('07. latest trading day', 'N/A')}"
#         )
#         return [document]

# class MappingComponent:
#     def __init__(self, mapping_file):
#         """
#         Initializes the Mapping Component to read the mapping file.
#         """
#         self.mapping = self.load_mapping(mapping_file)

#     def load_mapping(self, filename):
#         """
#         Loads the ticker mapping from a JSON file.
#         """
#         with open(filename, "r") as f:
#             mapping = json.load(f)
#         return mapping

#     def get_ticker_from_input(self, user_input, threshold=70):
#         """
#         Resolves the user input (company name) to the corresponding ticker symbol using fuzzy matching.
#         """
#         if user_input.upper() in self.mapping:
#             return user_input.upper()
#         companies = list(self.mapping.values())
#         result = process.extractOne(user_input, companies, scorer=fuzz.token_sort_ratio)
#         if result:
#             best_match, score, idx = result
#             if score >= threshold:
#                 tickers = list(self.mapping.keys())
#                 return tickers[idx]
#         return user_input.upper()  # Return the user input if no match is found

# # =======================
# # Flask API Setup
# # =======================
# app = Flask(__name__)

# @app.route('/api/financial-qa', methods=['GET'])
# def financial_qa():
#     """
#     API endpoint to get stock data based on user query (company name or ticker).
#     """
#     user_input = request.args.get('query')  # Get the query from the user
#     if not user_input:
#         return jsonify({"error": "No query provided"}), 400
    
#     # Load the ticker mapping from the uploaded JSON file
#     mapping_file = "/Users/yashdoshi/capstone_4/Capstone_Project/src/Agents/Investment_agent/ticker_mapping_full.json"  # Adjust to correct path
#     mapping_component = MappingComponent(mapping_file)
    
#     # Resolve user input to a ticker symbol
#     symbol = mapping_component.get_ticker_from_input(user_input)
#     print(f"Fetching data for ticker: {symbol}")

#     # Initialize the DataCollectionComponent
#     data_component = DataCollectionComponent()

#     # Fetch and preprocess stock data
#     stock_data = data_component.fetch_stock_data(symbol)
#     if stock_data:
#         documents = data_component.preprocess_stock_data(stock_data)
#         return jsonify({"answer": documents})  # Send the stock data details
#     else:
#         return jsonify({"answer": "No data found for the requested symbol."})

# if __name__ == '__main__':
#     app.run(debug=True)  

# import os
# import requests
# from flask import Flask, jsonify, request
# from transformers import pipeline
# import logging

# # Disable tokenizers parallelism warning
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Replace with your own Alpha Vantage API key
# ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'


# # =======================
# # Component 1: DataFetcherComponent
# # =======================
# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         """
#         Fetches real-time stock data for any stock symbol from Alpha Vantage API.

#         Args:
#             symbol (str): The stock symbol (e.g., AAPL, TSLA).

#         Returns:
#             dict: Stock data in JSON format.
#         """
#         logging.debug(f"Fetching real-time stock data for symbol: {symbol}")
#         params = {
#             'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#             'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#             'apikey': ALPHA_VANTAGE_API_KEY            
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()  # Return the data in JSON format
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# # =======================
# # Component 2: EmbedderComponent
# # =======================
# class EmbedderComponent:
#     def __init__(self):
#         logging.info("EmbedderComponent initialized")
#         # Initialize the Hugging Face pipeline for question-answering using a pre-trained model
#         self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased")
#         logging.debug("Question-answering pipeline initialized")

#     def generate_response(self, user_query, stock_data):
#         """
#         Generates a response to the user's query based on the stock data.

#         Args:
#             user_query (str): The user's query.
#             stock_data (dict): The stock data returned from Alpha Vantage API.

#         Returns:
#             str: The answer to the user's query, including all relevant stock data.
#         """
#         logging.debug(f"Generating response for query: {user_query}")
        
#         # Build the context string based on available stock data
#         context = ""

#         # If price is asked, provide the stock price
#         if "price" in user_query.lower():
#             context = f"The latest price of the stock is {stock_data['05. price']}."
#             logging.debug("User asked for price")
        
#         # If trend is asked, provide the change percentage
#         elif "trend" in user_query.lower():
#             trend = stock_data.get('10. change percent', 'N/A')
#             context = f"The trend for the stock is: {trend}."
#             logging.debug("User asked for trend")

#         # General information about the stock data
#         else:
#             context = (
#                 f"Stock Symbol: {stock_data['01. symbol']},\n"
#                 f"Open: {stock_data['02. open']},\n"
#                 f"High: {stock_data['03. high']},\n"
#                 f"Low: {stock_data['04. low']},\n"
#                 f"Price: {stock_data['05. price']},\n"
#                 f"Volume: {stock_data['06. volume']},\n"
#                 f"Latest Trading Day: {stock_data['07. latest trading day']},\n"
#                 f"Previous Close: {stock_data['08. previous close']},\n"
#                 f"Change: {stock_data['09. change']},\n"
#                 f"Change Percent: {stock_data['10. change percent']}\n"
#             )
#             logging.debug("User asked for general stock data")

#         # The model returns the answer based on the context
#         try:
#             result = self.qa_pipeline(question=user_query, context=context)
#             # Check if result is meaningful
#             if result and 'answer' in result:
#                 logging.info(f"Generated response: {result['answer']}")
#                 return result['answer']
#             else:
#                 logging.warning("Model did not generate a valid response, returning stock data directly.")
#                 print("Returning full stock data as a fallback:")  # Printing the full stock data for debugging
#                 return context  # If model doesn't provide a valid answer, return full stock data
#         except Exception as err:
#             logging.error(f"Error generating response: {err}")
#             return "Sorry, I couldn't process your query."


# # =======================
# # Component 3: QueryHandlerComponent
# # =======================
# class QueryHandlerComponent:
#     def __init__(self, data_fetcher, embedder):
#         logging.info("QueryHandlerComponent initialized")
#         self.data_fetcher = data_fetcher
#         self.embedder = embedder

#     def handle_query(self, user_query):
#         """Handles the user query and returns the most relevant stock data."""
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400  # Ensure two values are returned

#         stock_symbol = user_query.strip().upper()  # Makes the input uppercase
#         logging.debug(f"Handling query for stock symbol: {stock_symbol}")

#         # Fetch the stock data
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)
#         logging.debug(f"Fetched stock data: {stock_data}")

#         if stock_data:
#             # Generate response based on the user's query
#             response = self.embedder.generate_response(user_query, stock_data['Global Quote'])
#             return {"answer": response}, 200  # Return response and status code
#         else:
#             logging.error("Unable to fetch stock data.")
#             return {"error": "Unable to fetch stock data."}, 500  # Return error response and status code


# # =======================
# # Component 4: FinancialQAApp (Main app)
# # =======================
# class FinancialQAApp:
#     def __init__(self):
#         logging.info("FinancialQAApp initialized")
#         # Initialize all components
#         self.data_fetcher = DataFetcherComponent()
#         self.embedder = EmbedderComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher, self.embedder)

#     def run(self):
#         """
#         Runs the Flask app and sets up the route for query handling.
#         """
#         logging.debug("Setting up query route...")

#         # Route for handling queries about stock prices/trends
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')  # Retrieve the query from the request
#             logging.debug(f"Received query: {user_query}")  # Log the query

#             if user_query:
#                 logging.debug("Processing query...")
#                 response, status_code = self.query_handler.handle_query(user_query)  # This will unpack correctly now
#                 logging.debug(f"Response: {response}")
#                 return jsonify(response), status_code
#             else:
#                 logging.warning("No query parameter provided.")
#                 return jsonify({"error": "No query parameter provided."}), 400

#         # Root route for the app, returning a simple welcome message
#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"  # Custom message for the root


# # =======================
# # Main Execution
# # =======================
# if __name__ == '__main__':
#     logging.info("Starting Financial QA App")
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)


# import os
# import requests
# from flask import Flask, jsonify, request
# from transformers import pipeline
# import logging

# # Disable tokenizers parallelism warning
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Replace with your own Alpha Vantage API key
# ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'


# # =======================
# # Component 1: DataFetcherComponent
# # =======================
# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         """
#         Fetches real-time stock data for any stock symbol from Alpha Vantage API.

#         Args:
#             symbol (str): The stock symbol (e.g., AAPL, TSLA).

#         Returns:
#             dict: Stock data in JSON format.
#         """
#         logging.debug(f"Fetching real-time stock data for symbol: {symbol}")
#         params = {
#             'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#             'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#             'apikey': ALPHA_VANTAGE_API_KEY            
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()  # Return the data in JSON format
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# # =======================
# # Component 2: EmbedderComponent
# # =======================
# class EmbedderComponent:
#     def __init__(self):
#         logging.info("EmbedderComponent initialized")
#         # Initialize the Hugging Face pipeline for question-answering using a pre-trained model
#         self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased")
#         logging.debug("Question-answering pipeline initialized")

#     def generate_response(self, user_query, stock_data):
#         """
#         Generates a response to the user's query based on the stock data.

#         Args:
#             user_query (str): The user's query.
#             stock_data (dict): The stock data returned from Alpha Vantage API.

#         Returns:
#             str: The answer to the user's query, including all relevant stock data.
#         """
#         logging.debug(f"Generating response for query: {user_query}")
        
#         # Build the context string based on available stock data
#         context = ""

#         # If price is asked, provide the stock price
#         if "price" in user_query.lower():
#             context = f"The latest price of the stock is {stock_data['05. price']}."
#             logging.debug("User asked for price")
        
#         # If trend is asked, provide the change percentage
#         elif "trend" in user_query.lower():
#             trend = stock_data.get('10. change percent', 'N/A')
#             context = f"The trend for the stock is: {trend}."
#             logging.debug("User asked for trend")

#         # General information about the stock data
#         else:
#             context = (
#                 f"Stock Symbol: {stock_data['01. symbol']},\n"
#                 f"Open: {stock_data['02. open']},\n"
#                 f"High: {stock_data['03. high']},\n"
#                 f"Low: {stock_data['04. low']},\n"
#                 f"Price: {stock_data['05. price']},\n"
#                 f"Volume: {stock_data['06. volume']},\n"
#                 f"Latest Trading Day: {stock_data['07. latest trading day']},\n"
#                 f"Previous Close: {stock_data['08. previous close']},\n"
#                 f"Change: {stock_data['09. change']},\n"
#                 f"Change Percent: {stock_data['10. change percent']}\n"
#             )
#             logging.debug("User asked for general stock data")

#         # The model returns the answer based on the context
#         try:
#             result = self.qa_pipeline(question=user_query, context=context)
#             # Check if result is meaningful
#             if result and 'answer' in result:
#                 logging.info(f"Generated response: {result['answer']}")
#                 return result['answer']
#             else:
#                 logging.warning("Model did not generate a valid response, returning full stock data directly.")
#                 return context  # If model doesn't provide a valid answer, return full stock data
#         except Exception as err:
#             logging.error(f"Error generating response: {err}")
#             return "Sorry, I couldn't process your query."


# # =======================
# # Component 3: QueryHandlerComponent
# # =======================
# class QueryHandlerComponent:
#     def __init__(self, data_fetcher, embedder):
#         logging.info("QueryHandlerComponent initialized")
#         self.data_fetcher = data_fetcher
#         self.embedder = embedder

#     def handle_query(self, user_query):
#         """Handles the user query and returns the most relevant stock data."""
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400  # Ensure two values are returned

#         stock_symbol = user_query.strip().upper()  # Makes the input uppercase
#         logging.debug(f"Handling query for stock symbol: {stock_symbol}")

#         # Fetch the stock data
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)
#         logging.debug(f"Fetched stock data: {stock_data}")

#         if stock_data:
#             # Generate response based on the user's query
#             response = self.embedder.generate_response(user_query, stock_data['Global Quote'])
#             return {"answer": response}, 200  # Return response and status code
#         else:
#             logging.error("Unable to fetch stock data.")
#             return {"error": "Unable to fetch stock data."}, 500  # Return error response and status code


# # =======================
# # Component 4: FinancialQAApp (Main app)
# # =======================
# class FinancialQAApp:
#     def __init__(self):
#         logging.info("FinancialQAApp initialized")
#         # Initialize all components
#         self.data_fetcher = DataFetcherComponent()
#         self.embedder = EmbedderComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher, self.embedder)

#     def run(self):
#         """
#         Runs the Flask app and sets up the route for query handling.
#         """
#         logging.debug("Setting up query route...")

#         # Route for handling queries about stock prices/trends
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')  # Retrieve the query from the request
#             logging.debug(f"Received query: {user_query}")  # Log the query

#             if user_query:
#                 logging.debug("Processing query...")
#                 response, status_code = self.query_handler.handle_query(user_query)  # This will unpack correctly now
#                 logging.debug(f"Response: {response}")
#                 return jsonify(response), status_code
#             else:
#                 logging.warning("No query parameter provided.")
#                 return jsonify({"error": "No query parameter provided."}), 400

#         # Root route for the app, returning a simple welcome message
#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"  # Custom message for the root


# # =======================
# # Main Execution
# # =======================
# if __name__ == '__main__':
#     logging.info("Starting Financial QA App")
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)

# import os
# import requests
# from flask import Flask, jsonify, request
# import logging

# # Disable tokenizers parallelism warning
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Replace with your own Alpha Vantage API key
# ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'


# # =======================
# # Component 1: DataFetcherComponent
# # =======================
# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         """
#         Fetches real-time stock data for any stock symbol from Alpha Vantage API.

#         Args:
#             symbol (str): The stock symbol (e.g., AAPL, TSLA).

#         Returns:
#             dict: Stock data in JSON format.
#         """
#         logging.debug(f"Fetching real-time stock data for symbol: {symbol}")
#         params = {
#             'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#             'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#             'apikey': ALPHA_VANTAGE_API_KEY            
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()  # Return the data in JSON format
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# # =======================
# # Component 2: QueryHandlerComponent
# # =======================
# class QueryHandlerComponent:
#     def __init__(self, data_fetcher):
#         logging.info("QueryHandlerComponent initialized")
#         self.data_fetcher = data_fetcher

#     def handle_query(self, user_query):
#         """Handles the user query and returns the most relevant stock data."""
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400  # Ensure two values are returned

#         stock_symbol = user_query.strip().upper()  # Makes the input uppercase
#         logging.debug(f"Handling query for stock symbol: {stock_symbol}")

#         # Fetch the stock data
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)
#         logging.debug(f"Fetched stock data: {stock_data}")

#         if stock_data:
#             # Extract the stock data directly from the API response
#             global_quote = stock_data.get('Global Quote', {})
#             if global_quote:
#                 response = {
#                     "symbol": global_quote.get('01. symbol', 'N/A'),
#                     "open": global_quote.get('02. open', 'N/A'),
#                     "high": global_quote.get('03. high', 'N/A'),
#                     "low": global_quote.get('04. low', 'N/A'),
#                     "price": global_quote.get('05. price', 'N/A'),
#                     "volume": global_quote.get('06. volume', 'N/A'),
#                     "latest_trading_day": global_quote.get('07. latest trading day', 'N/A'),
#                     "previous_close": global_quote.get('08. previous close', 'N/A'),
#                     "change": global_quote.get('09. change', 'N/A'),
#                     "change_percent": global_quote.get('10. change percent', 'N/A')
#                 }
#                 return jsonify(response), 200  # Return stock data as JSON
#             else:
#                 logging.error("No 'Global Quote' data found in the response.")
#                 return {"error": "Unable to fetch valid stock data."}, 500
#         else:
#             logging.error("Unable to fetch stock data.")
#             return {"error": "Unable to fetch stock data."}, 500  # Return error response


# # =======================
# # Component 3: FinancialQAApp (Main app)
# # =======================
# class FinancialQAApp:
#     def __init__(self):
#         logging.info("FinancialQAApp initialized")
#         # Initialize all components
#         self.data_fetcher = DataFetcherComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher)

#     def run(self):
#         """
#         Runs the Flask app and sets up the route for query handling.
#         """
#         logging.debug("Setting up query route...")

#         # Route for handling queries about stock prices/trends
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')  # Retrieve the query from the request
#             logging.debug(f"Received query: {user_query}")  # Log the query

#             if user_query:
#                 logging.debug("Processing query...")
#                 response, status_code = self.query_handler.handle_query(user_query)  # This will unpack correctly now
#                 logging.debug(f"Response: {response}")
#                 return response, status_code
#             else:
#                 logging.warning("No query parameter provided.")
#                 return jsonify({"error": "No query parameter provided."}), 400

#         # Root route for the app, returning a simple welcome message
#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"  # Custom message for the root


# # =======================
# # Main Execution
# # =======================
# if __name__ == '__main__':
#     logging.info("Starting Financial QA App")
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)


# import os
# import requests
# from flask import Flask, jsonify, request
# import logging
# from flask_cors import CORS  # Import CORS to enable cross-origin requests

# # Disable tokenizers parallelism warning
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Replace with your own Alpha Vantage API key
# ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'


# # =======================
# # Component 1: DataFetcherComponent
# # =======================
# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         """
#         Fetches real-time stock data for any stock symbol from Alpha Vantage API.

#         Args:
#             symbol (str): The stock symbol (e.g., AAPL, TSLA).

#         Returns:
#             dict: Stock data in JSON format.
#         """
#         logging.debug(f"Fetching real-time stock data for symbol: {symbol}")
#         params = {
#             'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#             'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#             'apikey': ALPHA_VANTAGE_API_KEY            
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()  # Return the data in JSON format
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# # =======================
# # Component 2: QueryHandlerComponent
# # =======================
# class QueryHandlerComponent:
#     def __init__(self, data_fetcher):
#         logging.info("QueryHandlerComponent initialized")
#         self.data_fetcher = data_fetcher

#     def handle_query(self, user_query):
#         """Handles the user query and returns the most relevant stock data."""
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400  # Ensure two values are returned

#         stock_symbol = user_query.strip().upper()  # Makes the input uppercase
#         logging.debug(f"Handling query for stock symbol: {stock_symbol}")

#         # Fetch the stock data
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)
#         logging.debug(f"Fetched stock data: {stock_data}")

#         if stock_data:
#             # Extract the stock data directly from the API response
#             global_quote = stock_data.get('Global Quote', {})
#             if global_quote:
#                 response = {
#                     "symbol": global_quote.get('01. symbol', 'N/A'),
#                     "open": global_quote.get('02. open', 'N/A'),
#                     "high": global_quote.get('03. high', 'N/A'),
#                     "low": global_quote.get('04. low', 'N/A'),
#                     "price": global_quote.get('05. price', 'N/A'),
#                     "volume": global_quote.get('06. volume', 'N/A'),
#                     "latest_trading_day": global_quote.get('07. latest trading day', 'N/A'),
#                     "previous_close": global_quote.get('08. previous close', 'N/A'),
#                     "change": global_quote.get('09. change', 'N/A'),
#                     "change_percent": global_quote.get('10. change percent', 'N/A')
#                 }
#                 return jsonify(response), 200  # Return stock data as JSON
#             else:
#                 logging.error("No 'Global Quote' data found in the response.")
#                 return {"error": "Unable to fetch valid stock data."}, 500
#         else:
#             logging.error("Unable to fetch stock data.")
#             return {"error": "Unable to fetch stock data."}, 500  # Return error response


# # =======================
# # Component 3: FinancialQAApp (Main app)
# # =======================
# class FinancialQAApp:
#     def __init__(self):
#         logging.info("FinancialQAApp initialized")
#         # Initialize all components
#         self.data_fetcher = DataFetcherComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher)

#     def run(self):
#         """
#         Runs the Flask app and sets up the route for query handling.
#         """
#         logging.debug("Setting up query route...")

#         # Route for handling queries about stock prices/trends
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')  # Retrieve the query from the request
#             logging.debug(f"Received query: {user_query}")  # Log the query

#             if user_query:
#                 logging.debug("Processing query...")
#                 response, status_code = self.query_handler.handle_query(user_query)  # This will unpack correctly now
#                 logging.debug(f"Response: {response}")
#                 return response, status_code
#             else:
#                 logging.warning("No query parameter provided.")
#                 return jsonify({"error": "No query parameter provided."}), 400

#         # Root route for the app, returning a simple welcome message
#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"  # Custom message for the root


# # =======================
# # Main Execution
# # =======================
# if __name__ == '__main__':
#     logging.info("Starting Financial QA App")
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)

# import os
# import requests
# from flask import Flask, jsonify, request
# import logging
# from flask_cors import CORS  # Import CORS to enable cross-origin requests

# # Disable tokenizers parallelism warning
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Replace with your own Alpha Vantage API key
# ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'


# # =======================
# # Component 1: DataFetcherComponent
# # =======================
# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         """
#         Fetches real-time stock data for any stock symbol from Alpha Vantage API.

#         Args:
#             symbol (str): The stock symbol (e.g., AAPL, TSLA).

#         Returns:
#             dict: Stock data in JSON format.
#         """
#         logging.debug(f"Fetching real-time stock data for symbol: {symbol}")
#         params = {
#             'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#             'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#             'apikey': ALPHA_VANTAGE_API_KEY            
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()  # Return the data in JSON format
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# # =======================
# # Component 2: QueryHandlerComponent
# # =======================
# class QueryHandlerComponent:
#     def __init__(self, data_fetcher):
#         logging.info("QueryHandlerComponent initialized")
#         self.data_fetcher = data_fetcher

#     def handle_query(self, user_query):
#         """Handles the user query and returns the most relevant stock data."""
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400  # Ensure two values are returned

#         stock_symbol = user_query.strip().upper()  # Makes the input uppercase
#         logging.debug(f"Handling query for stock symbol: {stock_symbol}")

#         # Fetch the stock data
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)
#         logging.debug(f"Fetched stock data: {stock_data}")

#         if stock_data:
#             # Extract the stock data directly from the API response
#             global_quote = stock_data.get('Global Quote', {})
#             if global_quote:
#                 response = {
#                     "symbol": global_quote.get('01. symbol', 'N/A'),
#                     "open": global_quote.get('02. open', 'N/A'),
#                     "high": global_quote.get('03. high', 'N/A'),
#                     "low": global_quote.get('04. low', 'N/A'),
#                     "price": global_quote.get('05. price', 'N/A'),
#                     "volume": global_quote.get('06. volume', 'N/A'),
#                     "latest_trading_day": global_quote.get('07. latest trading day', 'N/A'),
#                     "previous_close": global_quote.get('08. previous close', 'N/A'),
#                     "change": global_quote.get('09. change', 'N/A'),
#                     "change_percent": global_quote.get('10. change percent', 'N/A')
#                 }
#                 return jsonify(response), 200  # Return stock data as JSON
#             else:
#                 logging.error("No 'Global Quote' data found in the response.")
#                 return {"error": "Unable to fetch valid stock data."}, 500
#         else:
#             logging.error("Unable to fetch stock data.")
#             return {"error": "Unable to fetch stock data."}, 500  # Return error response


# # =======================
# # Component 3: FinancialQAApp (Main app)
# # =======================
# class FinancialQAApp:
#     def __init__(self):
#         logging.info("FinancialQAApp initialized")
#         # Initialize all components
#         self.data_fetcher = DataFetcherComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher)

#     def run(self):
#         """
#         Runs the Flask app and sets up the route for query handling.
#         """
#         logging.debug("Setting up query route...")

#         # Route for handling queries about stock prices/trends
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')  # Retrieve the query from the request
#             logging.debug(f"Received query: {user_query}")  # Log the query

#             if user_query:
#                 logging.debug("Processing query...")
#                 response, status_code = self.query_handler.handle_query(user_query)  # This will unpack correctly now
#                 logging.debug(f"Response: {response}")
#                 return response, status_code
#             else:
#                 logging.warning("No query parameter provided.")
#                 return jsonify({"error": "No query parameter provided."}), 400

#         # Root route for the app, returning a simple welcome message
#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"  # Custom message for the root


# # =======================
# # Main Execution
# # =======================
# if __name__ == '__main__':
#     logging.info("Starting Financial QA App")
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)

# from flask import Flask, jsonify, request
# from flask_cors import CORS  # Import CORS to allow cross-origin requests
# import logging
# import os
# import requests

# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# # Initialize the Flask app
# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app, resources={"/api/*": {"origins": "*"}})  # Allow all domains for now

# logging.basicConfig(level=logging.DEBUG)

# ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'


# class DataFetcherComponent:
#     def __init__(self):
#         self.url = "https://www.alphavantage.co/query"
#         logging.info("DataFetcherComponent initialized")

#     def fetch_real_time_stock_data(self, symbol):
#         params = {
#             'function': 'GLOBAL_QUOTE',
#             'symbol': symbol,
#             'apikey': ALPHA_VANTAGE_API_KEY
#         }

#         try:
#             response = requests.get(self.url, params=params)
#             response.raise_for_status()
#             logging.info(f"Successfully fetched stock data for {symbol}")
#             return response.json()
#         except requests.exceptions.HTTPError as err:
#             logging.error(f"HTTP error occurred: {err}")
#         except Exception as err:
#             logging.error(f"An error occurred: {err}")
#         return None


# class QueryHandlerComponent:
#     def __init__(self, data_fetcher):
#         self.data_fetcher = data_fetcher

#     def handle_query(self, user_query):
#         if not user_query:
#             return {"error": "No query parameter provided."}, 400

#         stock_symbol = user_query.strip().upper()
#         stock_data = self.data_fetcher.fetch_real_time_stock_data(stock_symbol)

#         if stock_data:
#             global_quote = stock_data.get('Global Quote', {})
#             if global_quote:
#                 response = {
#                     "symbol": global_quote.get('01. symbol', 'N/A'),
#                     "open": global_quote.get('02. open', 'N/A'),
#                     "high": global_quote.get('03. high', 'N/A'),
#                     "low": global_quote.get('04. low', 'N/A'),
#                     "price": global_quote.get('05. price', 'N/A'),
#                     "volume": global_quote.get('06. volume', 'N/A'),
#                     "latest_trading_day": global_quote.get('07. latest trading day', 'N/A'),
#                     "previous_close": global_quote.get('08. previous close', 'N/A'),
#                     "change": global_quote.get('09. change', 'N/A'),
#                     "change_percent": global_quote.get('10. change percent', 'N/A')
#                 }
#                 return jsonify(response), 200
#             else:
#                 return {"error": "Unable to fetch valid stock data."}, 500
#         else:
#             return {"error": "Unable to fetch stock data."}, 500


# class FinancialQAApp:
#     def __init__(self):
#         self.data_fetcher = DataFetcherComponent()
#         self.query_handler = QueryHandlerComponent(self.data_fetcher)

#     def run(self):
#         @app.route('/api/financial-qa', methods=['GET'])
#         def query():
#             user_query = request.args.get('query')
#             if user_query:
#                 response, status_code = self.query_handler.handle_query(user_query)
#                 return response, status_code
#             else:
#                 return jsonify({"error": "No query parameter provided."}), 400

#         @app.route('/')
#         def home():
#             return "Welcome to the Financial QA API!"


# if __name__ == '__main__':
#     app_instance = FinancialQAApp()
#     app_instance.run()
#     app.run(debug=True)

import yfinance as yf
import numpy as np
import pandas as pd
import torch
import re
import os
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, List, Union

# Configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class StockDataProcessor:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.historical_data: Dict[str, pd.DataFrame] = {}

    def fetch_data(self, years: int = 5) -> pd.DataFrame:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        for ticker in self.tickers:
            try:
                data = yf.Ticker(ticker)
                df = data.history(start=start_date, end=end_date, auto_adjust=True)
                
                if df.empty:
                    continue
                    
                df = self._calculate_features(df)
                df['ticker'] = ticker
                self.historical_data[ticker] = df
                
            except Exception as e:
                continue
        
        if not self.historical_data:
            raise ValueError("No valid stock data was fetched")
            
        return pd.concat(self.historical_data.values())

    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df['returns'] = df['Close'].pct_change()
        df['sma_10'] = df['Close'].rolling(10).mean()
        df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['Close'].values)
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        return df.dropna()

    @staticmethod
    def _calculate_rsi(prices: np.ndarray, window: int = 14) -> np.ndarray:
        deltas = np.diff(prices)
        seed = deltas[:window+1]
        up = seed[seed >= 0].sum()/window
        down = -seed[seed < 0].sum()/window
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:window] = 100. - 100./(1.+rs)
        
        for i in range(window, len(prices)):
            delta = deltas[i-1]
            upval = delta if delta > 0 else 0.
            downval = -delta if delta < 0 else 0.
            up = (up*(window-1) + upval)/window
            down = (down*(window-1) + downval)/window
            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)
            
        return rsi

class FinancialPredictor:
    def __init__(self, tickers: List[str], model_dir: str = "./saved_model"):
        self.tickers = tickers
        self.model_dir = model_dir
        self.data_processor = StockDataProcessor(tickers)
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "yiyanghkust/finbert-tone",
            num_labels=2,
            ignore_mismatched_sizes=True
        )
        self.is_trained = False

    def train(self) -> bool:
        try:
            df = self.data_processor.fetch_data()
            texts, labels = self._create_text_prompts(df)
            
            encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")
            
            training_args = TrainingArguments(
                output_dir="./results",
                num_train_epochs=3,
                per_device_train_batch_size=8,
                evaluation_strategy="epoch",
                learning_rate=2e-5
            )
            
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=torch.utils.data.TensorDataset(
                    torch.tensor(encodings['input_ids']),
                    torch.tensor(labels)
                ),
                compute_metrics=lambda eval_pred: {
                    'accuracy': accuracy_score(*eval_pred)
                }
            )
            
            trainer.train()
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False

    def predict(self, ticker: str) -> Dict[str, Union[str, float]]:
        if ticker not in self.data_processor.historical_data:
            self.data_processor.fetch_data()
            
        df = self.data_processor.historical_data[ticker]
        latest = df.iloc[-1:].copy()
        
        text = self._create_text_prompts(latest)[0][0]
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confidence = probs[0][1].item()
        
        return {
            'ticker': ticker,
            'prediction': 'up' if confidence > 0.5 else 'down',
            'confidence': confidence,
            'last_close': float(latest['Close'].iloc[0]),
            'rsi': float(latest['rsi'].iloc[0]),
            'sma_10': float(latest['sma_10'].iloc[0]),
            'ema_50': float(latest['ema_50'].iloc[0])
        }

    def _create_text_prompts(self, df: pd.DataFrame) -> tuple:
        texts = []
        labels = []
        for _, row in df.iterrows():
            text = (
                f"Stock {row['ticker']} at {row.name.date()}: "
                f"Price ${row['Close']:.2f}, "
                f"RSI {row['rsi']:.1f}, "
                f"SMA10 ${row['sma_10']:.2f}, "
                f"EMA50 ${row['ema_50']:.2f}"
            )
            texts.append(text)
            labels.append(int(row['target']))
        return texts, labels

predictor = FinancialPredictor(["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "JPM", "NVDA", "WMT"])

@app.route('/api/analyze', methods=['GET'])
def analyze():
    ticker = request.args.get('ticker', '').upper()
    if not ticker or ticker not in predictor.tickers:
        return jsonify({'error': 'Invalid ticker'}), 400
    
    try:
        prediction = predictor.predict(ticker)
        stock = yf.Ticker(ticker).info
        return jsonify({
            'ticker': ticker,
            'prediction': prediction['prediction'],
            'confidence': prediction['confidence'],
            'price': prediction['last_close'],
            'rsi': prediction['rsi'],
            'sma_10': prediction['sma_10'],
            'ema_50': prediction['ema_50'],
            'pe_ratio': stock.get('trailingPE'),
            'market_cap': stock.get('marketCap'),
            'dividend_yield': stock.get('dividendYield')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks', methods=['GET'])
def stocks():
    return jsonify({'tickers': predictor.tickers})

if __name__ == '__main__':
    if not predictor.is_trained:
        predictor.train()
    app.run(host='0.0.0.0', port=5001, debug=False)