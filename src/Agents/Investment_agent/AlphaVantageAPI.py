# import requests
# import pandas as pd
# from transformers import RagTokenForGeneration, RagTokenizer, RagRetriever


# # Set up Alpha Vantage API key
# api_key = 'your API key'

# # Fetch daily stock data for a given symbol
# def fetch_stock_data(symbol, interval='daily'):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'interval': interval,
#         'apikey': api_key
#     }
#     response = requests.get(url, params=params)
#     data = response.json()
    
#     if "Time Series (Daily)" in data:
#         stock_data = pd.DataFrame(data['Time Series (Daily)']).T
#         stock_data = stock_data.apply(pd.to_numeric)
#         return stock_data
#     else:
#         print("Error: Unable to fetch data")
#         return None

# # Example: Fetch data for Tesla (TSLA)
# tesla_data = fetch_stock_data("TSLA")
# print(tesla_data.head())


# # Load the RAG model and tokenizer
# model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq")
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
# retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="custom")

# # Sample query
# query = "What is the risk level of Tesla stock?"

# # Tokenize the query
# input_ids = tokenizer(query, return_tensors="pt").input_ids

# # Generate response using RAG model
# generated_ids = model.generate(input_ids=input_ids, num_beams=4)
# generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

# print(generated_text)










# import requests
# import pandas as pd
# from datasets import Dataset
# import faiss
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration


# # Define the API key and URL
# api_key = 'your API key'
# symbol = 'AAPL'  # Change this to the symbol you're interested in
# url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

# # Send the request
# response = requests.get(url)
# data = response.json()

# # Extract the time series data (if it exists)
# if 'Time Series (Daily)' in data:
#     time_series = data['Time Series (Daily)']
# else:
#     print("Error: Unable to fetch data.")
#     time_series = {}

# # Convert the time series data into a pandas DataFrame
# df = pd.DataFrame.from_dict(time_series, orient='index')
# df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]

# # Convert the index (date) to a datetime object
# df.index = pd.to_datetime(df.index)

# # Convert the DataFrame into a list of documents (text representation)
# documents = df.apply(lambda row: f"Date: {row.name}, Open: {row['1. open']}, High: {row['2. high']}, Low: {row['3. low']}, Close: {row['4. close']}, Volume: {row['5. volume']}", axis=1).tolist()

# # Create the dataset
# dataset = Dataset.from_dict({"text": documents})

# # Save the dataset to disk
# dataset.save_to_disk("/Users/nemi/Documents/Capstone_Project")

# # Convert the documents into numerical vectors (embeddings)
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by faiss
# X = np.float32(X)

# # Create the FAISS index
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the FAISS index to disk
# faiss.write_index(index, "/Users/nemi/Documents/Capstone_Project/index.faiss")

# # Load the retriever with the saved index and dataset
# retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="custom", dataset_path="dataset_path", index_path="index_path")

# # Initialize the tokenizer
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")

# # Sample query (e.g., "What was the closing price of AAPL on 2025-02-07?")
# question = "What was the closing price of AAPL on 2025-02-07?"

# # Tokenize the query
# inputs = tokenizer(question, return_tensors="pt")

# # Use the retriever to fetch relevant documents
# retrieved_docs = retriever.retrieve(inputs['input_ids'])

# # Now, you can pass these retrieved documents to the RAG model to generate a response.

# # Load the RAG model
# model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

# # Generate the answer based on the retrieved documents
# outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)

# # Decode the output to get the answer
# decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
# print(decoded_output)













# import requests
# import pandas as pd
# import yfinance as yf
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration

# # Alpha Vantage API key and endpoint
# api_key = 'your API key'
# symbol = 'AAPL'  # Example: Change this to any stock symbol
# url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

# # Fetch data from Alpha Vantage API
# response = requests.get(url)
# data = response.json()

# # Extract the time series data (if it exists)
# if 'Time Series (Daily)' in data:
#     time_series = data['Time Series (Daily)']
# else:
#     print("Error: Unable to fetch data.")
#     time_series = {}

# # Convert the time series data into a pandas DataFrame
# df = pd.DataFrame.from_dict(time_series, orient='index')
# df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]

# # Convert the index (date) to a datetime object
# df.index = pd.to_datetime(df.index)

# # Display the stock data
# # print(df.head())

# # Function to fetch stock data from Yahoo Finance
# def get_yahoo_stock_data(symbol):
#     stock = yf.Ticker(symbol)
#     data = stock.history(period="5d")  # Get the last 5 days of stock data
#     data.index = data.index.tz_localize(None)  # Make Yahoo data timezone-naive
#     return data

# # Example usage
# symbol = 'AAPL'  # Replace with user input or desired stock symbol
# yahoo_data = get_yahoo_stock_data(symbol)
# # print(yahoo_data)

# # Fetch data from both Alpha Vantage and Yahoo Finance
# alpha_vantage_df = df  # From previous code
# yahoo_data = get_yahoo_stock_data(symbol)  # From Yahoo Finance

# # Normalize both DataFrames to have the same column names for merging
# alpha_vantage_df = alpha_vantage_df.rename(columns={
#     '1. open': 'Open',
#     '2. high': 'High',
#     '3. low': 'Low',
#     '4. close': 'Close',
#     '5. volume': 'Volume'
# })

# # Merge the data on the date index
# merged_data = pd.merge(alpha_vantage_df, yahoo_data[['Open', 'High', 'Low', 'Close', 'Volume']], 
#                        how='inner', left_index=True, right_index=True, suffixes=('_AV', '_Yahoo'))

# # print(merged_data.head())

# def get_stock_data(user_input):
#     # If user input is a stock name (e.g., Apple), we need to map it to a ticker symbol
#     stock_name_to_symbol = {
#         'Apple': 'AAPL',
#         'Microsoft': 'MSFT',
#         'Tesla': 'TSLA',
#         # Add more stock name-to-symbol mappings as needed
#     }
    
#     # Check if user input is a valid stock name
#     if user_input in stock_name_to_symbol:
#         symbol = stock_name_to_symbol[user_input]
#     else:
#         symbol = user_input  # Assume it's already a ticker symbol
    
#     # Fetch data from Alpha Vantage and Yahoo Finance
#     alpha_vantage_df = get_alpha_vantage_data(symbol)
#     yahoo_data = get_yahoo_stock_data(symbol)
    
#     # Merge both datasets
#     merged_data = merge_stock_data(alpha_vantage_df, yahoo_data)
    
#     return merged_data

# def get_alpha_vantage_data(symbol):
#     url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
#     response = requests.get(url)
#     data = response.json()
#     if 'Time Series (Daily)' in data:
#         time_series = data['Time Series (Daily)']
#         df = pd.DataFrame.from_dict(time_series, orient='index')
#         df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]
#         df.index = pd.to_datetime(df.index)
#         return df.rename(columns={
#             '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'
#         })
#     return pd.DataFrame()

# def merge_stock_data(alpha_vantage_df, yahoo_data):
#     merged_data = pd.merge(alpha_vantage_df, yahoo_data[['Open', 'High', 'Low', 'Close', 'Volume']], 
#                            how='inner', left_index=True, right_index=True, suffixes=('_AV', '_Yahoo'))
#     return merged_data

# # Example user input (stock name or ticker symbol)
# user_input = input("Enter stock name or ticker symbol (e.g., AAPL or Apple): ")
# stock_data = get_stock_data(user_input)
# print(stock_data)

# # Initialize the retriever (You will need a pre-trained model here)
# retriever = RagRetriever.from_pretrained("facebook/rag-token-nq")

# # Initialize the tokenizer
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")

# # Function to query the stock data
# def query_stock_data(question):
#     inputs = tokenizer(question, return_tensors="pt")
    
#     # Retrieve the most relevant documents (stock data in this case)
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])

#     # Load the model
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

#     # Generate the answer based on the retrieved documents
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     return decoded_output

# # Example user query
# query = "What is the closing price of AAPL on 2025-02-07?"
# answer = query_stock_data(query)
# print(answer)










# import requests
# import pandas as pd
# import yfinance as yf
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
# import faiss
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset

# # Alpha Vantage API key and endpoint
# api_key = 'your API key'
# symbol = 'AAPL'  # Example: Change this to any stock symbol
# url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

# # Fetch data from Alpha Vantage API
# response = requests.get(url)
# data = response.json()

# # Extract the time series data (if it exists)
# if 'Time Series (Daily)' in data:
#     time_series = data['Time Series (Daily)']
# else:
#     print("Error: Unable to fetch data.")
#     time_series = {}

# # Convert the time series data into a pandas DataFrame
# df = pd.DataFrame.from_dict(time_series, orient='index')
# df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]

# # Convert the index (date) to a datetime object
# df.index = pd.to_datetime(df.index)

# # Function to fetch stock data from Yahoo Finance
# def get_yahoo_stock_data(symbol):
#     stock = yf.Ticker(symbol)
#     data = stock.history(period="5d")  # Get the last 5 days of stock data
#     data.index = data.index.tz_localize(None)  # Make Yahoo data timezone-naive
#     return data

# # Fetch data from both Alpha Vantage and Yahoo Finance
# alpha_vantage_df = df  # From previous code
# yahoo_data = get_yahoo_stock_data(symbol)  # From Yahoo Finance

# # Normalize both DataFrames to have the same column names for merging
# alpha_vantage_df = alpha_vantage_df.rename(columns={
#     '1. open': 'Open',
#     '2. high': 'High',
#     '3. low': 'Low',
#     '4. close': 'Close',
#     '5. volume': 'Volume'
# })

# # Merge the data on the date index
# merged_data = pd.merge(alpha_vantage_df, yahoo_data[['Open', 'High', 'Low', 'Close', 'Volume']], 
#                        how='inner', left_index=True, right_index=True, suffixes=('_AV', '_Yahoo'))

# # Convert the merged data into a list of documents (text representation)
# documents = merged_data['Close_AV'].astype(str).tolist()  # Using the 'Close_AV' column as an example

# # Convert to a TF-IDF vector representation
# vectorizer = TfidfVectorizer(stop_words='english')
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by faiss
# X = np.float32(X)

# # Create the FAISS index
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Define paths to save dataset and index
# dataset_path = "/Users/nemi/Documents/Capstone_Project/dataset"
# index_path = "/Users/nemi/Documents/Capstone_Project/index_file.index"

# # Save the FAISS index
# faiss.write_index(index, index_path)

# # Save the dataset for later use in the retriever
# dataset = Dataset.from_dict({"text": documents})
# dataset.save_to_disk(dataset_path)

# # Now, initialize the retriever with the custom dataset and index
# retriever = RagRetriever.from_pretrained(
#     "facebook/rag-token-nq",
#     index_name="custom",
#     dataset_path=dataset_path,
#     index_path=index_path
# )

# # Initialize the tokenizer
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")

# # Function to query the stock data
# def query_stock_data(question):
#     inputs = tokenizer(question, return_tensors="pt")
    
#     # Retrieve the most relevant documents (stock data in this case)
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])

#     # Load the model
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
    
#     # Generate the answer based on the retrieved documents
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
    
#     # Decode the output to get the answer
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     return decoded_output

# # Example user query (Replace with any stock-related query)
# query = "What is the closing price of AAPL on 2025-02-07?"
# answer = query_stock_data(query)
# print(answer)

# # Function to get stock data based on user input (name or ticker symbol)
# def get_stock_data(user_input):
#     # If user input is a stock name (e.g., Apple), we need to map it to a ticker symbol
#     stock_name_to_symbol = {
#         'Apple': 'AAPL',
#         'Microsoft': 'MSFT',
#         'Tesla': 'TSLA',
#         # Add more stock name-to-symbol mappings as needed
#     }
    
#     # Check if user input is a valid stock name
#     if user_input in stock_name_to_symbol:
#         symbol = stock_name_to_symbol[user_input]
#     else:
#         symbol = user_input  # Assume it's already a ticker symbol
    
#     # Fetch data from Alpha Vantage and Yahoo Finance
#     alpha_vantage_df = get_alpha_vantage_data(symbol)
#     yahoo_data = get_yahoo_stock_data(symbol)
    
#     # Merge both datasets
#     merged_data = merge_stock_data(alpha_vantage_df, yahoo_data)
    
#     return merged_data

# # Function to fetch Alpha Vantage data
# def get_alpha_vantage_data(symbol):
#     url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
#     response = requests.get(url)
#     data = response.json()
#     if 'Time Series (Daily)' in data:
#         time_series = data['Time Series (Daily)']
#         df = pd.DataFrame.from_dict(time_series, orient='index')
#         df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]
#         df.index = pd.to_datetime(df.index)
#         return df.rename(columns={
#             '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'
#         })
#     return pd.DataFrame()

# # Function to merge stock data from both sources
# def merge_stock_data(alpha_vantage_df, yahoo_data):
#     merged_data = pd.merge(alpha_vantage_df, yahoo_data[['Open', 'High', 'Low', 'Close', 'Volume']], 
#                            how='inner', left_index=True, right_index=True, suffixes=('_AV', '_Yahoo'))
#     return merged_data

# # Example user input (stock name or ticker symbol)
# user_input = input("Enter stock name or ticker symbol (e.g., AAPL or Apple): ")
# stock_data = get_stock_data(user_input)
# print(stock_data)










# import requests
# import openai

# API_KEY = 'your API key'  
# openai.api_key = 'your API key'


# def fetch_real_time_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'GLOBAL_QUOTE',
#         'symbol': symbol,  # Directly use the stock symbol provided
#         'apikey': API_KEY  # Your Vantage API key
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Function to fetch weekly stock data
# def fetch_weekly_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_WEEKLY_ADJUSTED',
#         'symbol': symbol,  # Use the stock symbol directly
#         'apikey': API_KEY  # Your Vantage API key
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching weekly data for {symbol}: {response.status_code}")
#         return None

# # Function to generate LLM response based on data
# def generate_response(user_query, stock_data):
#     prompt = f"User Query: {user_query}\n\nStock Data: {stock_data}\n\nResponse:"
    
#     # Updated API call to use the correct ChatCompletion endpoint
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",  # Use the appropriate model (e.g., gpt-3.5-turbo)
#         messages=[
#             {"role": "system", "content": "You are a helpful financial assistant."},
#             {"role": "user", "content": prompt}
#         ]
#     )
    
#     return response['choices'][0]['message']['content']

# # User input: stock symbol
# stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").upper()

# # User query: asking for the price or trend
# user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

# if "price" in user_query:
#     # Fetch real-time stock data
#     stock_data = fetch_real_time_stock_data(stock_symbol)
#     print(f"Raw data from API: {stock_data}")  # Print raw API response for debugging
#     if stock_data and 'Global Quote' in stock_data:
#         latest_price = stock_data['Global Quote'].get('05. price', 'N/A')
#         response = generate_response(user_query, f"The latest price of {stock_symbol} is {latest_price}")
#         print(response)
#     else:
#         print("Error: Stock data not available or 'Global Quote' missing.")

# elif "trend" in user_query:
#     # Fetch weekly stock data
#     weekly_data = fetch_weekly_stock_data(stock_symbol)
#     print(f"Raw weekly data from API: {weekly_data}")  # Print raw API response for debugging
#     if weekly_data and 'Weekly Adjusted Time Series' in weekly_data:
#         trend_data = weekly_data['Weekly Adjusted Time Series']
#         last_week_price = float(list(trend_data.values())[0]['4. close'])
#         prev_week_price = float(list(trend_data.values())[1]['4. close'])
#         price_change = ((last_week_price - prev_week_price) / prev_week_price) * 100
#         response = generate_response(user_query, f"{stock_symbol} stock has changed by {price_change:.2f}% over the past week.")
#         print(response)
#     else:
#         print("Error: Weekly stock data not available or 'Weekly Adjusted Time Series' missing.")









# import requests
# import pandas as pd
# from transformers import pipeline

# # Alpha Vantage API key
# API_KEY = 'your API key'

# # Function to fetch real-time stock data from Alpha Vantage
# def fetch_real_time_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'GLOBAL_QUOTE',
#         'symbol': symbol,  # Directly use the stock symbol provided
#         'apikey': API_KEY  # Your Vantage API key
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Function to fetch weekly stock data from Alpha Vantage
# def fetch_weekly_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_WEEKLY_ADJUSTED',
#         'symbol': symbol,  # Use the stock symbol directly
#         'apikey': API_KEY  # Your Vantage API key
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching weekly data for {symbol}: {response.status_code}")
#         return None

# # Function to generate the response using Hugging Face's model
# def generate_response(user_query, stock_data):
#     # Load the question-answering pipeline from Hugging Face
#     qa_pipeline = pipeline("question-answering")
    
#     # Use the stock data as context for the model
#     prompt = f"User Query: {user_query}\n\nStock Data: {stock_data}\n\nResponse:"
    
#     result = qa_pipeline({
#         'context': stock_data,
#         'question': user_query
#     })
    
#     return result['answer']

# # Function to get stock data for a user query
# def get_stock_data(user_input):
#     # Fetch data from Alpha Vantage API based on user input (stock symbol)
#     stock_symbol = user_input.upper()
    
#     # Fetch real-time stock data
#     stock_data = fetch_real_time_stock_data(stock_symbol)
#     if stock_data:
#         latest_price = stock_data['Global Quote']['05. price']
#         stock_info = f"The latest price of {stock_symbol} is {latest_price}"
#         return stock_info
#     else:
#         return "Error: Stock data not available."

# # Example of how to use the functions
# user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ")
# stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").upper()

# # Get stock data (price or trend)
# stock_data = get_stock_data(stock_symbol)

# # Generate an answer based on stock data using Hugging Face model
# if stock_data != "Error: Stock data not available.":
#     answer = generate_response(user_query, stock_data)
#     print(f"Answer: {answer}")
# else:
#     print("Error: Stock data not available.")












import requests
from transformers import pipeline

 
API_KEY = 'your API key'# Replace with your own Vantage API key

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