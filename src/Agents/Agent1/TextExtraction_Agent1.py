import pytesseract
from pdf2image import convert_from_bytes
import re
import pandas as pd
import spacy
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message="torch.set_default_tensor_type() is deprecated")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    images = convert_from_bytes(pdf_bytes)
    text = "\n".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
    return text

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

def main():
    pdf_path = "creditcard_statement.pdf"  
    text = extract_text_from_pdf(pdf_path)
    print("Extracted Text:\n", text[:1000])

    transactions_df = extract_transactions(text)
    if transactions_df.empty:
        print("\nNo transactions found in the text. Please check the OCR output or the format of the PDF.")
    else:
        print("\nExtracted Transactions:")
        print(transactions_df.head())

        transactions_df = extract_store_names(transactions_df)
        print("\nTransactions with Store Names:")
        print(transactions_df.head())

        transactions_df.to_csv("transactions_with_categories.csv", index=False)
        print("\nTransactions saved to 'transactions_with_categories.csv'.")

if __name__ == "__main__":
    main()

