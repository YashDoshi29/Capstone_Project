import pytesseract
from pdf2image import convert_from_bytes
import re
import pandas as pd
import spacy
import warnings
import os
from pydantic import BaseModel, field_validator
from typing import List
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_community.llms import Ollama

warnings.filterwarnings("ignore", category=UserWarning, message="torch.set_default_tensor_type() is deprecated")

nlp = spacy.load("en_core_web_sm")

# PDF Processing
class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        images = convert_from_bytes(pdf_bytes)
        text = "\n".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
        return text

# Extract Transactions
class TransactionExtractor:
    @staticmethod
    def extract_transactions(text):
        lines = text.split("\n")
        transactions = []
        transaction_pattern = re.compile(
            r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+([A-Za-z0-9\s\*\.\#\-\/]+)\s+([A-Za-z0-9\s\*\.\#\-\/]+)\s+\d+\s+\d+\s+(-?[\d,]+\.\d{2})"
        )
        for line in lines:
            match = transaction_pattern.search(line)
            if match:
                posting_date, transaction_date, description, state, amount = match.groups()
                amount = float(amount.replace(",", ""))  
                
                # Only append transactions with positive amounts
                if amount > 0:
                    transactions.append({
                        "Posting Date": posting_date.strip(),
                        "Transaction Date": transaction_date.strip(),
                        "Description": description.strip(),
                        "State": state.strip(),
                        "Amount": amount
                    })
        return pd.DataFrame(transactions)

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

# Ollama Model
class OllamaAPI:
    def __init__(self, model_name="llama3.2"):
        self.llm = Ollama(model=model_name)

    def query(self, prompt):
        return self.llm.invoke(prompt)

# Category Mapper with Optimized LLM Query
class CategoryMapper:
    @staticmethod
    def map_categories(df, llm_api):
        unique_stores = df["Store"].unique()
        query = (
            "You are an AI assistant specializing in financial transaction classification. "
            "Given the following store names, provide an appropriate spending category for each. "
            "Categories include: Food and Drinks, Shopping, Travel, Services, Health and Wellness, Entertainment, etc.\n"
            "Provide your response in the format: 'Store - Category'.\n\n"
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

# Fuzzy Matcher
class FuzzyMatcher:
    @staticmethod
    def fuzzy_match(value, choices, threshold=80):
        match, score = process.extractOne(value, choices)
        return match if score >= threshold else None

# Response Validator
class ResponseChecks(BaseModel):
    data: List[str]

    @field_validator("data")
    def check(cls, value):
        for item in value:
            assert " - " in item, f"Invalid format: {item}"
        return value

# Visualization
class TransactionVisualizer:
    @staticmethod
    def visualize_category_distribution(df_merged):
        plt.style.use('dark_background')
        category_amounts = df_merged.groupby('Category')['Amount'].sum()

        plt.figure(figsize=(8, 8))
        def autopct_func(pct, allvalues):
            absolute = round(pct / 100. * sum(allvalues), 2)
            return f'{pct:.2f}%\n${absolute:.2f}'

        plt.pie(category_amounts, labels=category_amounts.index, autopct=lambda pct: autopct_func(pct, category_amounts),
                startangle=120, colors=plt.cm.Paired.colors, textprops={'color': 'white'}) 

        plt.title('Spending Distribution by Category', color='white', fontsize=16, pad=20)
        plt.axis('equal')  
        plt.show()

# Main Processor
class CreditCardStatementProcessor:
    def __init__(self, pdf_path, llm_api):
        self.pdf_path = pdf_path
        self.llm_api = llm_api

    def process(self):
        text = PDFProcessor.extract_text_from_pdf(self.pdf_path)
        transactions_df = TransactionExtractor.extract_transactions(text)

        if transactions_df.empty:
            print("No transactions found.")
            return

        transactions_df = StoreNameExtractor.extract_store_names(transactions_df)
        transactions_df.to_csv("transactions_with_categories.csv", index=False)

        df = pd.read_csv("transactions_with_categories.csv")
        categories_df = CategoryMapper.map_categories(df, self.llm_api)

        df['Fuzzy_Match_Description'] = df['Store'].apply(lambda x: FuzzyMatcher.fuzzy_match(x, categories_df['Transaction'].unique()))
        df_merged = pd.merge(df, categories_df, left_on='Fuzzy_Match_Description', right_on='Transaction', how='left').drop(columns=['Fuzzy_Match_Description'])

        TransactionVisualizer.visualize_category_distribution(df_merged)

# Main Execution
if __name__ == "__main__":
    pdf_path = "creditcard_statement.pdf"
    llm_api = OllamaAPI()
    processor = CreditCardStatementProcessor(pdf_path, llm_api)
    processor.process()
