from flask import Flask, jsonify, request
import json
import requests
from rapidfuzz import process, fuzz

# --- API Keys ---
ALPHA_VANTAGE_API_KEY = 'O30LC68NVP5U8YSQ'  # Alpha Vantage API Key

# ============================
# COMPONENTS
# ============================

class DataCollectionComponent:
    def fetch_stock_data(self, symbol):
        """
        Fetches stock data for a given ticker symbol from Alpha Vantage API.
        """
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(url, params=params)

        # Debugging: print the entire response to see the returned data
        print(f"API Response for {symbol}: {response.status_code}")
        print(response.json())  # Print the full response

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching stock data for {symbol}: {response.status_code}")
            return None

    def preprocess_stock_data(self, stock_data):
        """
        Processes the fetched stock data to extract meaningful information.
        """
        if not stock_data:
            return []
        quote_data = stock_data.get('Global Quote', {})  # Corrected key from the response
        if not quote_data:
            print("No stock data found.")
            return []
        document = (
            f"Stock Data - Symbol: {quote_data.get('01. symbol', 'N/A')}, "
            f"Open: {quote_data.get('02. open', 'N/A')}, "
            f"High: {quote_data.get('03. high', 'N/A')}, "
            f"Low: {quote_data.get('04. low', 'N/A')}, "
            f"Price: {quote_data.get('05. price', 'N/A')}, "
            f"Volume: {quote_data.get('06. volume', 'N/A')}, "
            f"Latest Trading Day: {quote_data.get('07. latest trading day', 'N/A')}"
        )
        return [document]

class MappingComponent:
    def __init__(self, mapping_file):
        """
        Initializes the Mapping Component to read the mapping file.
        """
        self.mapping = self.load_mapping(mapping_file)

    def load_mapping(self, filename):
        """
        Loads the ticker mapping from a JSON file.
        """
        with open(filename, "r") as f:
            mapping = json.load(f)
        return mapping

    def get_ticker_from_input(self, user_input, threshold=70):
        """
        Resolves the user input (company name) to the corresponding ticker symbol using fuzzy matching.
        """
        if user_input.upper() in self.mapping:
            return user_input.upper()
        companies = list(self.mapping.values())
        result = process.extractOne(user_input, companies, scorer=fuzz.token_sort_ratio)
        if result:
            best_match, score, idx = result
            if score >= threshold:
                tickers = list(self.mapping.keys())
                return tickers[idx]
        return user_input.upper()  # Return the user input if no match is found

# =======================
# Flask API Setup
# =======================
app = Flask(__name__)

@app.route('/api/financial-qa', methods=['GET'])
def financial_qa():
    """
    API endpoint to get stock data based on user query (company name or ticker).
    """
    user_input = request.args.get('query')  # Get the query from the user
    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    
    # Load the ticker mapping from the uploaded JSON file
    mapping_file = "/Users/yashdoshi/capstone_4/Capstone_Project/src/Agents/Investment_agent/ticker_mapping_full.json"  # Adjust to correct path
    mapping_component = MappingComponent(mapping_file)
    
    # Resolve user input to a ticker symbol
    symbol = mapping_component.get_ticker_from_input(user_input)
    print(f"Fetching data for ticker: {symbol}")

    # Initialize the DataCollectionComponent
    data_component = DataCollectionComponent()

    # Fetch and preprocess stock data
    stock_data = data_component.fetch_stock_data(symbol)
    if stock_data:
        documents = data_component.preprocess_stock_data(stock_data)
        return jsonify({"answer": documents})  # Send the stock data details
    else:
        return jsonify({"answer": "No data found for the requested symbol."})

if __name__ == '__main__':
    app.run(debug=True)  