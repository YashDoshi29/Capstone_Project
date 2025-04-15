
# import requests
# import pandas as pd

# def fetch_stock_data(symbol, api_key):
#     # Fetch data from Alpha Vantage API
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': api_key
#     }
#     response = requests.get(url, params=params)
    
#     # Check for a successful response
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     # Check if the expected data exists in the response
#     time_series = stock_data.get('Time Series (Daily)', {})
    
#     if not time_series:
#         print("No time series data found in the response.")
#         return []
    
#     documents = []
    
#     # Process each day's stock data
#     for date, data in time_series.items():
#         # Ensure each key exists before accessing it to avoid KeyError
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')
        
#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
    
#     return documents

# def main():
#     api_key = 'O30LC68NVP5U8YSQ'
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
    
#     # Fetch stock data
#     stock_data = fetch_stock_data(symbol, api_key)
    
#     if stock_data:
#         # Preprocess the fetched data
#         documents = preprocess_data(stock_data)
        
#         if documents:
#             print("Processed documents:")
#             for doc in documents[:5]:  # Show the first 5 documents
#                 print(doc)
#         else:
#             print("No valid stock data found.")
#     else:
#         print("Failed to fetch stock data.")

# if __name__ == "__main__":
#     main()

#####################################################################################

# import requests
# import pandas as pd
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration

# # Define your Alpha Vantage API key
# API_KEY = 'O30LC68NVP5U8YSQ'

# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents

# def setup_rag_model():
#     retriever = RagRetriever.from_pretrained("facebook/rag-token-nq")
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output

# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     if documents:
#         retriever, tokenizer, model = setup_rag_model()
#         response = query_stock_data(user_query, retriever, tokenizer, documents)
#         print("Answer:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()

###############################################################################

# import requests
# import pandas as pd
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
# import faiss
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset


# # Fetch data from Alpha Vantage
# API_KEY = 'O30LC68NVP5U8YSQ'

# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents


# symbol = "AAPL"
# stock_data = fetch_stock_data(symbol)
# documents = preprocess_data(stock_data)
# print(documents[:5])  # Show first 5 documents

# # Assuming 'documents' is the list of stock-related documents
# dataset = Dataset.from_dict({"text": documents})

# # Save the dataset to disk
# dataset.save_to_disk("stock_data")


# # Convert documents to numerical vectors using TF-IDF
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by FAISS
# X = np.float32(X)

# # Create a FAISS index (Flat L2 distance metric)
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the index to disk
# faiss.write_index(index, "stock_index.index")

# def setup_rag_model():
#     # Load the retriever, tokenizer, and model
#     retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="custom", index_path="/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/stock_index.index", dataset_path="/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent")
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# retriever, tokenizer, model = setup_rag_model()

# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
    
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output


# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     if documents:
#         retriever, tokenizer, model = setup_rag_model()
#         response = query_stock_data(user_query, retriever, tokenizer, documents)
#         print("Answer:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()


################################################################################
    
# import requests
# import faiss
# import numpy as np
# import pandas as pd
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset

# # Alpha Vantage API key and URL
# API_KEY = 'O30LC68NVP5U8YSQ'

# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents

# symbol = "AAPL"
# stock_data = fetch_stock_data(symbol)
# documents = preprocess_data(stock_data)
# print(documents[:5])  # Show first 5 documents

# # Convert documents to numerical vectors using TF-IDF
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by FAISS
# X = np.float32(X)

# # Create a FAISS index (Flat L2 distance metric)
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the index to disk
# faiss.write_index(index, "stock_index.index")

# # Save dataset
# dataset = Dataset.from_dict({"text": documents})
# dataset.save_to_disk("stock_data")

# def setup_rag_model():
#     retriever = RagRetriever.from_pretrained(
#         "facebook/rag-token-nq", 
#         index_name="custom", 
#         index_path="stock_index.index",  # Path to your FAISS index
#         dataset_path="stock_data"  # Path to your dataset
#     )
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# retriever, tokenizer, model = setup_rag_model()

# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
    
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output

# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     if documents:
#         retriever, tokenizer, model = setup_rag_model()
#         response = query_stock_data(user_query, retriever, tokenizer, documents)
#         print("Answer:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()


################################################################################

# import requests
# import faiss
# import numpy as np
# import pandas as pd
# from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset

# # Alpha Vantage API key and URL
# API_KEY = 'O30LC68NVP5U8YSQ'

# # Function to fetch stock data from Alpha Vantage API
# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Function to preprocess stock data into documents
# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents

# # Path setup
# dataset_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/dataset_path"  # Folder where dataset is saved
# index_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/index_path"  # Folder where FAISS index is saved

# symbol = "AAPL"
# stock_data = fetch_stock_data(symbol)
# documents = preprocess_data(stock_data)
# print(documents[:5])  # Show first 5 documents

# # Convert documents to numerical vectors using TF-IDF
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by FAISS
# X = np.float32(X)

# # Create a FAISS index (Flat L2 distance metric)
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the index to disk at the specified path
# # faiss.write_index(index, f"{index_path}/stock_index.index")

# # Save dataset at the specified path
# dataset = Dataset.from_dict({"text": documents})
# dataset.save_to_disk(dataset_path)

# # Save dataset
# dataset.save_to_disk(dataset_path)
# print(f"Dataset saved to {dataset_path}")

# # Save index
# faiss.write_index(index, f"{index_path}/stock_index.index")
# print(f"FAISS index saved!")

# # Setup RAG model with correct paths for the dataset and index
# def setup_rag_model():
#     retriever = RagRetriever.from_pretrained(
#         "facebook/rag-token-nq", 
#         index_name="custom", 
#         index_path='/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/index_path/stock_index.index',  # Path to your FAISS index
#         dataset_path='/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/dataset_path'  # Path to your dataset
#     )
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# retriever, tokenizer, model = setup_rag_model()

# # Function to query stock data
# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
    
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output

# # Main function
# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     if documents:
#         retriever, tokenizer, model = setup_rag_model()
#         response = query_stock_data(user_query, retriever, tokenizer, documents)
#         print("Answer:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()

################################################################################


# import requests
# import faiss
# import numpy as np
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset
# from transformers import RagRetriever, RagTokenizer, RagTokenForGeneration


# # Alpha Vantage API key and URL
# API_KEY = 'O30LC68NVP5U8YSQ'

# # Function to fetch stock data from Alpha Vantage API
# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Function to preprocess stock data into documents
# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents

# # Path setup
# dataset_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/dataset_path"  # Folder where dataset is saved
# index_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/index_path"  # Folder where FAISS index is saved

# # Fetch stock data and preprocess it
# symbol = "AAPL"
# stock_data = fetch_stock_data(symbol)
# documents = preprocess_data(stock_data)
# print(documents[:5])  # Show first 5 documents

# # Convert documents to numerical vectors using TF-IDF
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by FAISS
# X = np.float32(X)

# # Create a FAISS index (Flat L2 distance metric)
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the index to disk at the specified path
# faiss.write_index(index, f"{index_path}/stock_index.index")

# # Save dataset at the specified path
# dataset = Dataset.from_dict({"text": documents})
# dataset.save_to_disk(dataset_path)

# # Custom Retrieval Function
# def custom_retrieve(query, faiss_index, documents, vectorizer, top_k=3):
#     query_vector = vectorizer.transform([query]).toarray().astype(np.float32)
#     distances, indices = faiss_index.search(query_vector, top_k)
#     retrieved_docs = [documents[idx] for idx in indices[0]]
#     return retrieved_docs

# # Load GPT-2 for text generation
# model = GPT2LMHeadModel.from_pretrained("gpt2")
# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# # Function to generate a response using the retrieved documents and user query
# def generate_response(query, retrieved_docs):
#     input_text = query + "\n" + "\n".join(retrieved_docs)
#     inputs = tokenizer.encode(input_text, return_tensors="pt")
#     outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

# # Setup RAG Model function
# def setup_rag_model():
#     retriever = RagRetriever.from_pretrained(
#         "facebook/rag-token-nq", 
#         index_name="custom", 
#         index_path=f"{index_path}/stock_index.index",  # Path to your FAISS index
#         dataset_path=dataset_path  # Path to your dataset
#     )
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# # Function to query stock data
# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
    
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output

# # Main function
# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data and preprocess it
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     # Load FAISS index from disk
#     faiss_index = faiss.read_index(f"{index_path}/stock_index.index")

#     if documents:
#         retriever, tokenizer, model = setup_rag_model()
        
#         # Retrieve relevant documents using custom retrieval function
#         top_docs = custom_retrieve(user_query, faiss_index, documents, vectorizer)
        
#         # Generate and print the response
#         response = generate_response(user_query, top_docs)
#         print("Generated Response:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()


########################################################################################

# import multiprocessing
# multiprocessing.set_start_method('spawn', force=True)

# import os
# os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
# os.environ['TOKENIZERS_PARALLELISM'] = 'false'


# import requests
# import faiss
# import numpy as np
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# from transformers import RagRetriever, RagTokenizer, RagTokenForGeneration
# from sklearn.feature_extraction.text import TfidfVectorizer
# from datasets import Dataset

# # Alpha Vantage API key and URL
# API_KEY = 'O30LC68NVP5U8YSQ'

# # Function to fetch stock data from Alpha Vantage API
# def fetch_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'
#     params = {
#         'function': 'TIME_SERIES_DAILY',
#         'symbol': symbol,
#         'apikey': API_KEY
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Function to preprocess stock data into documents
# def preprocess_data(stock_data):
#     if not stock_data:
#         return []

#     time_series = stock_data.get('Time Series (Daily)', {})
#     if not time_series:
#         print("No time series data found in the response.")
#         return []

#     documents = []
#     for date, data in time_series.items():
#         open_price = data.get('1. open', 'N/A')
#         high_price = data.get('2. high', 'N/A')
#         low_price = data.get('3. low', 'N/A')
#         close_price = data.get('4. close', 'N/A')
#         volume = data.get('5. volume', 'N/A')

#         document = f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}"
#         documents.append(document)
#     return documents

# # Path setup
# dataset_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/dataset_path"  # Folder where dataset is saved
# index_path = "/Users/nemi/Documents/Capstone_Project/src/Agents/Investment_agent/index_path"  # Folder where FAISS index is saved

# # Fetch stock data and preprocess it
# symbol = "AAPL"
# stock_data = fetch_stock_data(symbol)
# documents = preprocess_data(stock_data)
# print(documents[:5])  # Show first 5 documents

# # Convert documents to numerical vectors using TF-IDF
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(documents).toarray()

# # Convert to float32 as required by FAISS
# X = np.float32(X)

# # Create a FAISS index (Flat L2 distance metric)
# index = faiss.IndexFlatL2(X.shape[1])  # L2 distance metric
# index.add(X)

# # Save the index to disk at the specified path
# faiss.write_index(index, f"{index_path}/stock_index.index")

# # Save dataset at the specified path
# dataset = Dataset.from_dict({"text": documents})
# # dataset.save_to_disk(dataset_path)

# # Custom Retrieval Function
# def custom_retrieve(query, faiss_index, documents, vectorizer, top_k=3):
#     query_vector = vectorizer.transform([query]).toarray().astype(np.float32)
#     distances, indices = faiss_index.search(query_vector, top_k)
#     retrieved_docs = [documents[idx] for idx in indices[0]]
#     return retrieved_docs

# # Load GPT-2 for text generation
# model = GPT2LMHeadModel.from_pretrained("gpt2")
# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# # Function to generate a response using the retrieved documents and user query
# def generate_response(query, retrieved_docs):
#     input_text = query + "\n" + "\n".join(retrieved_docs)
#     inputs = tokenizer.encode(input_text, return_tensors="pt")
#     outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

# # Setup RAG Model function
# def setup_rag_model():
#     retriever = RagRetriever.from_pretrained(
#         "facebook/rag-token-nq", 
#         index_name="custom", 
#         index_path=f"{index_path}/stock_index.index",  # Path to your FAISS index
#         dataset_path=dataset_path  # Path to your dataset
#     )
#     tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
#     model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
#     return retriever, tokenizer, model

# # Function to query stock data
# def query_stock_data(user_query, retriever, tokenizer, documents):
#     inputs = tokenizer(user_query, return_tensors="pt")
#     # Retrieve relevant documents based on the user's query
#     retrieved_docs = retriever.retrieve(inputs['input_ids'])
    
#     # Generate the response using the RAG model
#     outputs = model.generate(input_ids=inputs["input_ids"], decoder_start_token_id=model.config.pad_token_id)
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return decoded_output

# # Main function
# def main():
#     symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()

#     # Fetch stock data and preprocess it
#     stock_data = fetch_stock_data(symbol)
#     documents = preprocess_data(stock_data)

#     if documents:
#         # Load FAISS index from disk
#         index = faiss.read_index(f"{index_path}/stock_index.index")
        
#         retriever, tokenizer, model = setup_rag_model()
        
#         # Retrieve relevant documents using custom retrieval function
#         top_docs = custom_retrieve(user_query, index, documents, vectorizer)
        
#         # Generate and print the response
#         response = generate_response(user_query, top_docs)
#         print("Generated Response:", response)
#     else:
#         print("No data available for the given stock symbol.")

# if __name__ == "__main__":
#     main()



# import requests
# from transformers import pipeline

#  # Replace with your own Vantage API key

# # Fetching the real-time stock data for any stock symbol from the Alpha Vantage API
# def fetch_real_time_stock_data(symbol):
#     url = f'https://www.alphavantage.co/query'

#     params = {
#         'function': 'GLOBAL_QUOTE',  # 'GLOBAL_QUOTE' gets the latest data for a stock
#         'symbol': symbol,            # Stock symbol entered by the user (e.g., AAPL, TSLA)
#         'apikey': API_KEY            
#     }

#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         return response.json()  # Return the data in JSON format
#     else:
#         print(f"Error fetching data for {symbol}: {response.status_code}")
#         return None

# # Initialize the Hugging Face pipeline for question-answering using a pre-trained model
# qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased")

# # This function will now only return the relevant answer based on the user's query
# def generate_response(user_query, stock_data):
#     # Check if the user is asking about the price or trend
#     if "price" in user_query.lower():
#         # Only include the price in the context if the user asks for the price
#         context = f"The latest price of the stock is {stock_data['05. price']}"
#     elif "trend" in user_query.lower():
#         # Calculate the trend based on change percentage
#         trend = stock_data['10. change percent']
#         context = f"The trend for the stock is: {trend}"
#     else:
#         # Provide other data based on the user's query
#         context = f"Stock Data: {stock_data}"

#     # The model returns the answer based on the context
#     result = qa_pipeline(question=user_query, context=context)
#     return result['answer']

# # Main function combining everything
# def main():
#     stock_symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").upper()  # Makes the input uppercase
#     user_query = input("Ask a financial question (e.g., 'What is the price of AAPL stock?'): ").lower()  # Lowercase for flexibility

#     # Fetch the stock data
#     stock_data = fetch_real_time_stock_data(stock_symbol)

#     if stock_data:
#         print("Fetched stock data:", stock_data)  # You can remove this if you don't want to display all data

#         # Generate response based on the user's query
#         response = generate_response(user_query, stock_data['Global Quote'])  # Only pass the stock data part

#         # Print the response
#         print(response)
#     else:
#         print("Unable to fetch stock data.")

# if __name__ == "__main__":
#     main()

