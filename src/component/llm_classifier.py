from langchain_community.llms import Ollama
import pandas as pd
import re

llm = Ollama(model='llama3.2')

def extract_store_name(description):
    clean_name = re.sub(r"[^a-zA-Z\s]", "", description)
    words = clean_name.split()
    store_name = " ".join(words[:2])
    return store_name.strip().upper()

def categorize_transactions(transaction_names):
    response = llm.invoke(
        "Can you add an appropriate category to the following expenses? "
        "For example: Forever - Shopping, Auntie Annes - Food, etc."
        "Categories should be less than 4 words.\n" + transaction_names
    )
    
    response = response.split("\n")
    categories_df = pd.DataFrame({'Transaction vs category': response})

    if not all(" - " in item for item in response):
        raise ValueError("Unexpected response format from LLM!")

    categories_df[['Transaction', 'Category']] = categories_df['Transaction vs category'].str.split(' - ', expand=True)
    return categories_df
