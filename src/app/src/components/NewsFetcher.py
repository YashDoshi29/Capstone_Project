from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], methods=["GET", "POST", "OPTIONS"])

ALPHA_VANTAGE_API_KEY = "T684OLI0SYSBG3Y3"
GROQ_API_KEY = "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"
NEWS_JSON_FILE = "financial_news.json"

# Initialize the Sentence Transformer model for embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize the Groq client for completions
groq_client = Groq(api_key=GROQ_API_KEY)

def fetch_financial_news(urls):
    """
    Fetch financial news data from the given list of URLs and save it to a JSON file.
    """
    all_news_data = []

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            news_data = response.json()
            all_news_data.extend(news_data.get("feed", []))  
        else:
            print(f"Error: Failed to fetch news from {url}.")

    with open(NEWS_JSON_FILE, "w") as f:
        json.dump({"feed": all_news_data}, f, indent=4)

    return all_news_data

def load_news_data():
    """
    Load news data from a JSON file, or fetch it if not present.
    """
    if not os.path.exists(NEWS_JSON_FILE):
        print("News data file not found. Fetching news...")
        urls = [
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_VANTAGE_API_KEY}",
        ]
        news_data = fetch_financial_news(urls)
        if not news_data:
            raise FileNotFoundError("Could not fetch news data. Check API keys and connectivity.")

    with open(NEWS_JSON_FILE, "r") as f:
        data = json.load(f)

    articles = data.get("feed", [])
    documents = []

    for article in articles:
        title = article.get("title", "No Title")
        summary = article.get("summary", "No Summary")
        content = f"Title: {title}\nSummary: {summary}"
        documents.append(content)

    return documents

def create_vector_store():
    """
    Create a vector store by encoding the news documents and storing them in a FAISS index.
    """
    news_docs = load_news_data()
    
    embeddings = embedder.encode(news_docs, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, news_docs

# Create the vector store (FAISS index) and load the news documents
vector_store, news_docs = create_vector_store()

def retrieve_relevant_news(query, k=3):
    """
    Retrieve the most relevant news articles for a given query.
    Uses FAISS index to perform nearest neighbor search based on embeddings.
    """
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    distances, indices = vector_store.search(query_embedding, k)

    relevant_news = [news_docs[i] for i in indices[0] if i < len(news_docs)]
    return "\n".join(relevant_news)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    if "query" not in data:
        return jsonify({"error": "Missing 'query' in request"}), 400

    user_query = data["query"]

    # Get relevant news for the query
    context = retrieve_relevant_news(user_query, k=3)

    # Use Groq's API to generate a response based on relevant news
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[ 
            {"role": "system", "content": "You are a financial news assistant. Provide concise and relevant answers."},
            {"role": "user", "content": f"Here is relevant news:\n{context}\n\nAnswer my question: {user_query}"}
        ],
        temperature=0.7
    )

    return jsonify({"response": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)