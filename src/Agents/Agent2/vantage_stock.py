import requests
import openai


def fetch_real_time_stock_data(symbol):
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,  # Directly use the stock symbol provided
        'apikey': API_KEY  # Your Vantage API key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {symbol}: {response.status_code}")
        return None

# Function to fetch weekly stock data
def fetch_weekly_stock_data(symbol):
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_WEEKLY_ADJUSTED',
        'symbol': symbol,  # Use the stock symbol directly
        'apikey': API_KEY  # Your Vantage API key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weekly data for {symbol}: {response.status_code}")
        return None

# Function to generate LLM response based on data
def generate_response(user_query, stock_data):
    prompt = f"User Query: {user_query}\n\nStock Data: {stock_data}\n\nResponse:"
    
    # Updated API call to use the correct ChatCompletion endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model (e.g., gpt-3.5-turbo)
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

# User input: stock symbol
stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").upper()

# User query: asking for the price or trend
user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

if "price" in user_query:
    # Fetch real-time stock data
    stock_data = fetch_real_time_stock_data(stock_symbol)
    if stock_data:
        latest_price = stock_data['Global Quote']['05. price']
        response = generate_response(user_query, f"The latest price of {stock_symbol} is {latest_price}")
        print(response)

elif "trend" in user_query:
    # Fetch weekly stock data
    weekly_data = fetch_weekly_stock_data(stock_symbol)
    if weekly_data:
        # Simplified trend analysis
        trend_data = weekly_data['Weekly Adjusted Time Series']
        last_week_price = float(list(trend_data.values())[0]['4. close'])
        prev_week_price = float(list(trend_data.values())[1]['4. close'])
        price_change = ((last_week_price - prev_week_price) / prev_week_price) * 100
        response = generate_response(user_query, f"{stock_symbol} stock has changed by {price_change:.2f}% over the past week.")
        print(response)