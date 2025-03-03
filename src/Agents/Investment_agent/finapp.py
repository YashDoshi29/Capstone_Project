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
        Fetches daily stock data for a given ticker symbol from Alpha Vantage API.
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
        time_series = stock_data.get('Time Series (Daily)', {})  # Use the correct key from API response
        if not time_series:
            print("No time series data found.")
            return []
        documents = []
        for date, data in time_series.items():
            document = (
                f"Stock Data - Date: {date}, Open: {data['1. open']}, High: {data['2. high']}, "
                f"Low: {data['3. low']}, Close: {data['4. close']}, Volume: {data['5. volume']}"
            )
            documents.append(document)
        return documents

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
    mapping_file = "/path/to/your/ticker_mapping_full.json"  # Adjust to correct path
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
        return jsonify({"answer": documents[:5]})  # Send first 5 stock data entries
    else:
        return jsonify({"answer": "No data found for the requested symbol."})

if __name__ == '__main__':
    app.run(debug=True)  # Run Flask app on http://localhost:5000
