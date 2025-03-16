import os
import subprocess
from flask import Flask, request, jsonify, Response
import re
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from flask_cors import CORS
import requests
import json
import io
import csv
from fuzzywuzzy import process  
from pydantic import BaseModel, field_validator
import spacy
from typing import List

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)
nlp = spacy.load("en_core_web_sm")

GROQ_API_KEY = "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"  
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"

class GroqAPI:
    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name

    def query(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        try:
            response = requests.post(GROQ_API_URL, json=data, headers=headers)
            response.raise_for_status()
            response_json = response.json()

            print("🔍 Full LLM API Response:", response_json)

            choices = response_json.get("choices", [])
            if choices and "message" in choices[0]:
                return choices[0]["message"]["content"].strip()

            return ""

        except requests.RequestException as e:
            print("❌ LLM API Request Error:", e)
            return ""


llm_api = GroqAPI(GROQ_API_KEY, MODEL_NAME)

def extract_text_from_pdf(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    text = "\n".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
    return text

def extract_transactions(text):
    lines = text.split("\n")
    transactions = []

    transaction_pattern = re.compile(
        r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+([A-Za-z0-9\s\*\.\#\-\/]+)\s+\d+\s+\d+\s+(-?[\d,]+\.\d{2})(\s+[A-Za-z]*)?"
    )

    for line in lines:
        match = transaction_pattern.search(line)
        if match:
            posting_date, transaction_date, description, amount, state = match.groups()
            
            if amount is not None:
                amount = float(amount.replace(",", ""))
            else:
                continue  
           
            state = state.strip() if state else "N/A"

            transactions.append({
                "Posting Date": posting_date.strip(),
                "Transaction Date": transaction_date.strip(),
                "Description": description.strip(),
                "State": state,
                "Amount": amount
            })

    return pd.DataFrame(transactions)


class CategoryMapper:
    @staticmethod
    def map_categories(df, llm_api):
        unique_stores = df["Store"].unique()
        query = (
        "You are an AI assistant specializing in financial transaction classification. "
        "Given the following store names, classify each one into a predefined category. "
        "The available categories include common ones like: Food, Shopping, Travel, Services, Health, Entertainment, and others. "
        "Each category should be simple and relevant, like 'Food', 'Shopping', 'Online Shopping', 'Health', etc. "
        "If you are unsure about the category, choose the most relevant one based on common usage. "
        "Feel free to use other known categories that make sense for the store, such as 'Utilities', 'Education', 'Transportation', etc. "
        "Avoid using complex or ambiguous categories like 'Unknown' or 'GWU'. "
        "Provide your response in the format: 'Items - Category'."
)
        query += "\n".join(unique_stores)

        try:
            response = llm_api.query(query)
            categories = [line.strip() for line in response.split("\n") if " - " in line]
        except Exception as e:
            raise RuntimeError("Failed to communicate with LLM API. Ensure the service is running.") from e

        ResponseChecks(data=categories)
        
        categories_df = pd.DataFrame({'Transaction vs category': categories})
        categories_df[['Transaction', 'Category']] = categories_df['Transaction vs category'].str.split(' - ', expand=True)
        categories_df = categories_df.dropna()
        return categories_df

class FuzzyMatcher:
    @staticmethod
    def fuzzy_match(value, choices, threshold=80):
        match, score = process.extractOne(value, choices)
        return match if score >= threshold else None

class ResponseChecks(BaseModel):
    data: List[str]

    @field_validator("data")
    def check(cls, value):
        for item in value:
            assert " - " in item, f"Invalid format: {item}"
        return value

class StoreNameExtractor:
    @staticmethod
    def extract_store_names(df):
        def clean_store_name(description):
            doc = nlp(description)
            possible_names = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "FAC", "PRODUCT"]]
            if possible_names:
                return possible_names[0]
            return re.sub(r"[^A-Za-z0-9 ]", "", description).strip()

        df["Store"] = df["Description"].apply(clean_store_name)
        return df

class CreditCardStatementProcessor:
    def __init__(self, file_bytes, file_type, llm_api):
        self.file_bytes = file_bytes
        self.file_type = file_type
        self.llm_api = llm_api

    def process_pdf(self):
        text = extract_text_from_pdf(self.file_bytes)
        transactions_df = extract_transactions(text)

        if transactions_df.empty:
            print("No transactions found.")
            return

        transactions_df = StoreNameExtractor.extract_store_names(transactions_df) 
        transactions_df.to_csv("transactions_with_categories.csv", index=False)

        df = pd.read_csv("transactions_with_categories.csv")
        categories_df = CategoryMapper.map_categories(df, self.llm_api)

        df['Fuzzy_Match_Description'] = df['Store'].apply(lambda x: FuzzyMatcher.fuzzy_match(x, categories_df['Transaction'].unique()))
        df_merged = pd.merge(df, categories_df, left_on='Fuzzy_Match_Description', right_on='Transaction', how='left').drop(columns=['Fuzzy_Match_Description'])

        df_merged.to_csv("categorized_transactions.csv", index=False)

    def process_csv(self):
      
        df = pd.read_csv(io.BytesIO(self.file_bytes))
        categories_df = CategoryMapper.map_categories(df, self.llm_api)

        df['Fuzzy_Match_Description'] = df['Store'].apply(lambda x: FuzzyMatcher.fuzzy_match(x, categories_df['Transaction'].unique()))
        df_merged = pd.merge(df, categories_df, left_on='Fuzzy_Match_Description', right_on='Transaction', how='left').drop(columns=['Fuzzy_Match_Description'])

        df_merged.to_csv("categorized_transactions.csv", index=False)

    def process(self):
        if self.file_type == "pdf":
            self.process_pdf()
        elif self.file_type == "csv":
            self.process_csv()
        else:
            raise ValueError("Unsupported file type")

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            print("❌ No file part in request")
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            print("❌ No selected file")
            return jsonify({"error": "No selected file"}), 400

        file_extension = file.filename.split('.')[-1].lower()
        if file_extension == "pdf":
            file_type = "pdf"
        elif file_extension == "csv":
            file_type = "csv"
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        print(f"✅ File uploaded: {file.filename}")
        file_bytes = file.read()

        processor = CreditCardStatementProcessor(file_bytes, file_type, llm_api)
        processor.process()

        with open("categorized_transactions.csv", "r") as f:
            return Response(f.read(), content_type="text/csv")

    except Exception as e:
        print("❌ Server Error:", e)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
