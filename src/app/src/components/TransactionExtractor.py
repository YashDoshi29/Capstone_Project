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
import pdfplumber

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)
nlp = spacy.load("en_core_web_sm")

GROQ_API_KEY = "YOUR_API_KEY"  
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
            "temperature": 0.1
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

def extract_text_from_pdf(pdf_bytes, output_filename="extracted_text.txt"):
    """Extract text from PDF using pdfplumber for text-based PDFs or pytesseract for scanned PDFs.
    Saves the extracted text to a text file."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text()

            if all_text.strip(): 
                print("Text extracted using pdfplumber.")
            else:
                print("No text found using pdfplumber. Falling back to OCR...")
                images = convert_from_bytes(pdf_bytes)
                ocr_text = "\n".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
                all_text = ocr_text

            with open(output_filename, "w", encoding="utf-8") as output_file:
                output_file.write(all_text)

            print(f"Text successfully written to {output_filename}")
            return all_text
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return ""

EXCLUDED_KEYWORDS = [
    "Payment", "Credit Card Payment", "Autopay", "ACH Payment", "CC Payment",
    "Card Payment", "Statement Credit", "Balance Transfer", "Payments and Other Credits", "Interest Charged"
]

def extract_transactions(text):
    """Robust line-by-line transaction extraction using multiple patterns."""
    transactions = []

    boa_pattern = re.compile(
        r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.+?)\s+([A-Z]{2})(?:\s+\d{4}){1,2}\s+([-?\d,]+\.\d{2})"
    )

    chase_pattern = re.compile(
        r"(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})$"
    )

    cleaned_transactions = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = boa_pattern.search(line)
        if match:
            posting_date, transaction_date, description, state, amount = match.groups()
        else:
            match = chase_pattern.search(line)
            if match:
                transaction_date, description, amount = match.groups()
                posting_date = transaction_date
                state = ""
            else:
                continue  

        try:
            amount = float(amount.replace(",", ""))
            if amount < 0:
                continue  
        except ValueError:
            continue

        if any(keyword.lower() in description.lower() for keyword in EXCLUDED_KEYWORDS):
            continue

        cleaned_transactions.append({
            "Posting Date": posting_date.strip(),
            "Transaction Date": transaction_date.strip(),
            "Description": description.strip(),
            "State": state.strip(),
            "Amount": amount
        })

    return pd.DataFrame(cleaned_transactions)
class CategoryMapper:

    @staticmethod
    def map_categories(df, llm_api):
        unique_stores = df["Store"].dropna().unique().tolist()

        prompt = (
        "You are a transaction categorization assistant.\n"
        "Classify ONLY the following store names (provided below) into one of these predefined categories:\n"
        "'Food', 'Grocery', 'Shopping', 'Travel', 'Entertainment', 'Utilities', 'Services', 'Healthcare'.\n\n"
        "💡 Rules:\n"
        "- Use only the store names listed below. Do NOT invent or assume any store names.\n"
        "- If a store is clearly food-related (including Uber Eats), classify it as 'Food'.\n"
        "- If a store has 'IC*' in its name, classify it as 'Grocery'.\n"
        "- If a store matches Uber Trip or Lyft, classify it as 'Travel'.\n"
        "- Do not include extra text like 'Store list:' or commentary.\n"
        "- Return only mappings in this format: Store - Category (one per line).\n\n"
        "Here are the stores:\n" + "\n".join(unique_stores)
    )

        try:
            response = llm_api.query(prompt)
            print("🧠 Raw LLM Response:\n", response)
            mappings = []
            for line in response.split("\n"):
                if " - " in line:
                    store, category = map(str.strip, line.split(" - ", 1))
                    mappings.append({"Transaction": store, "Category": category})
        except Exception as e:
            raise RuntimeError("LLM categorization failed") from e

        return pd.DataFrame(mappings)


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
            description = re.sub(r"[^A-Za-z0-9\s\*#&'\-.,]", "", description)  
            description = re.sub(r"\s{2,}", " ", description).strip()  
            return description

        df["Store"] = df["Description"].apply(clean_store_name)
        return df


class CreditCardStatementProcessor:
    def __init__(self, file_bytes, llm_api):
        self.file_bytes = file_bytes
        self.llm_api = llm_api

    def process(self):
        text = extract_text_from_pdf(self.file_bytes)
        transactions_df = extract_transactions(text)

        if transactions_df.empty:
            print("No transactions found.")
            return

        transactions_df = StoreNameExtractor.extract_store_names(transactions_df)
        transactions_df.to_csv("transactions_with_categories.csv", index=False)

        df = pd.read_csv("transactions_with_categories.csv")
        categories_df = CategoryMapper.map_categories(df, self.llm_api)

        df['Fuzzy_Match_Description'] = df['Store'].apply(
            lambda x: FuzzyMatcher.fuzzy_match(x, categories_df['Transaction'].unique())
        )
        df_merged = pd.merge(df, categories_df, left_on='Fuzzy_Match_Description', right_on='Transaction', how='left')
        df_merged.drop(columns=['Fuzzy_Match_Description'], inplace=True)
        df_merged.drop_duplicates(inplace=True)
        df_merged.to_csv("categorized_transactions.csv", index=False)

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file.filename.split('.')[-1].lower() != "pdf":
            return jsonify({"error": "Only PDF files are supported."}), 400

        file_bytes = file.read()
        processor = CreditCardStatementProcessor(file_bytes, llm_api)
        processor.process()

        with open("categorized_transactions.csv", "r") as f:
            return Response(f.read(), content_type="text/csv")

    except Exception as e:
        print("❌ Server Error:", e)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050, use_reloader=False)
