from component.pdf_extractor import extract_text_from_pdf
from component.transaction_extractor import extract_transactions, extract_store_names
from component.llm_classifier import categorize_transactions, extract_store_name
from component.fuzzy_matcher import fuzzy_match
from component.visualizer import plot_spending_distribution
from component.utils_helpers import save_csv, load_csv
import pandas as pd

def main():
    pdf_path = "creditcard_statement.pdf"  
    text = extract_text_from_pdf(pdf_path)

    transactions_df = extract_transactions(text)
    if transactions_df.empty:
        print("No transactions found in the text. Please check the OCR output.")
        return

    transactions_df = extract_store_names(transactions_df)
    save_csv(transactions_df, "transactions_with_categories.csv")

    transactions_df["Store"] = transactions_df["Description"].apply(extract_store_name)
    unique_stores = transactions_df["Store"].unique()

    transaction_names = ", ".join(unique_stores)
    categories_df = categorize_transactions(transaction_names)
    
    categories_df.dropna(inplace=True)
    transactions_df["Fuzzy_Match_Description"] = transactions_df["Description"].apply(lambda x: fuzzy_match(x, categories_df["Transaction"].unique()))
    df_merged = pd.merge(transactions_df, categories_df, left_on="Fuzzy_Match_Description", right_on="Transaction", how="left")

    df_merged.drop(columns=["Fuzzy_Match_Description"], inplace=True)
    save_csv(df_merged, "categorized_transactions.csv")

    plot_spending_distribution(df_merged)

if __name__ == "__main__":
    main()
