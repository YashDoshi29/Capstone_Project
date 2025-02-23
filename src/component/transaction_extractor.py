import re
import pandas as pd
import spacy

def extract_transactions(text):
    lines = text.split("\n")
    transactions = []
    transaction_pattern = re.compile(
        r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+([A-Za-z0-9\s\*\.\#\-\/]+)\s+([A-Za-z0-9\s\*\.\#\-\/]+)\s+\d+\s+\d+\s+([\d,]+\.\d{2})"
    )
    for line in lines:
        match = transaction_pattern.search(line)
        if match:
            posting_date, transaction_date, description, state, amount = match.groups()
            amount = float(amount.replace(",", ""))
            transactions.append({
                "Posting Date": posting_date.strip(),
                "Transaction Date": transaction_date.strip(),
                "Description": description.strip(),
                "State": state.strip(),
                "Amount": amount
            })
    return pd.DataFrame(transactions)

def extract_store_names(df):
    nlp = spacy.load("en_core_web_sm")
    def get_store_name(description):
        doc = nlp(description)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "GPE", "FAC", "PRODUCT"]:
                return ent.text
        return description
    df["Store"] = df["Description"].apply(get_store_name)
    return df
