import requests
from transformers import pipeline

 # Replace with your own Vantage API key

# Fetching the real-time stock data for any stock symbol from the Alpha Vantage API
def fetch_real_time_stock_data(symbol):
    url = f'https://www.alphavantage.co/query'

    params = {
        'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
        'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
        'apikey': API_KEY            
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()  # Return the data in JSON format
    else:
        print(f"Error fetching data for {symbol}: {response.status_code}")
        return None

# Initialize the Hugging Face pipeline for question-answering using a pre-trained model
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased")

# This function will now only return the relevant answer based on the user's query
def generate_response(user_query, stock_data):
    # Check if the user is asking about the price or trend
    if "price" in user_query.lower():
        # Only include the price in the context if the user asks for the price
        context = f"The latest price of the stock is {stock_data['05. price']}"
    elif "trend" in user_query.lower():
        # Calculate the trend based on change percentage
        trend = stock_data['10. change percent']
        context = f"The trend for the stock is: {trend}"
    else:
        # Provide other data based on the user's query
        context = f"Stock Data: {stock_data}"

    # The model returns the answer based on the context
    result = qa_pipeline(question=user_query, context=context)
    return result['answer']

# Main function combining everything
def main():
    stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").upper()  # Makes the input uppercase
    user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()  # Lowercase for flexibility

    # Fetch the stock data
    stock_data = fetch_real_time_stock_data(stock_symbol)

    if stock_data:
        print("Fetched stock data:", stock_data)  # You can remove this if you don't want to display all data

        # Generate response based on the user's query
        response = generate_response(user_query, stock_data['Global Quote'])  # Only pass the stock data part

        # Print the response
        print(response)
    else:
        print("Unable to fetch stock data.")

if __name__ == "__main__":
    main()
