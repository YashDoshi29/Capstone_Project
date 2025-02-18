
#%%
from langchain_community.llms import Ollama
llm = Ollama(model='llama3.2')

import pandas as pd
df = pd.read_csv("transactions_with_categories.csv")
df.head()

import re
def extract_store_name(description):
    clean_name = re.sub(r"[^a-zA-Z\s]", "", description)
    words = clean_name.split()
    
    store_name = " ".join(words[:2])
    return store_name.strip().upper()  

df["Store"] = df["Description"].apply(extract_store_name)
unique_stores = df["Store"].unique()
unique_stores

query = "Can you add an appropriate category next to each of the following stores? For example, Forever - Shopping, Auntie Annes - Food, etc.: Respond with a list of categories separated by '-'.\n"
query += ", ".join(unique_stores)

response = llm.invoke(query)
categories = response.split("\n")


#%%
def hop(start, stop, step):
    for i in range(start, stop, step):
        yield i
    yield stop

index_list = list(hop(0, len(unique_stores), 17))
index_list

from pydantic import BaseModel, field_validator
from typing import List

class ResponseChecks(BaseModel):
    data: List[str]

    @field_validator("data")
    def check(cls, value):
        for item in value:
            if len(item) > 0:
                assert "-" in item, "String does not contain hyphen."

ResponseChecks(data = ['Hello - World', 'Hello - there!'])

#%% 
def categorize_transactions(transaction_names, llm):
    response = llm.invoke(
        "Can you add an appropriate category to the following expenses. For example: "
        "Forever - Shopping, Auntie Annes - Food, etc."
        "Categories should be less than 4 words. " + transaction_names
    )
    print("Raw LLM Response:", response) 

    response = response.split("\n")

    blank_indexes = [index for index in range(len(response)) if response[index] == '']
    if len(blank_indexes) == 1:
        response = response[(blank_indexes[0] + 1):]
    else:
        response = response[(blank_indexes[0] + 1): blank_indexes[1]]

    print("Processed Response:", response)  

    ResponseChecks(data=response)
    
    categories_df = pd.DataFrame({'Transaction vs category': response})

    if not all(" - " in item for item in response):
        raise ValueError("Unexpected response format from LLM!")

    categories_df[['Transaction', 'Category']] = categories_df['Transaction vs category'].str.split(' - ', expand=True)
    return categories_df

#%%
categories_data = []
max_tries = 2

for i in range(0, len(index_list) - 1):
    transaction_names = unique_stores[index_list[i]:index_list[i + 1]]
    transaction_names = ', '.join(transaction_names)

    # Retry mechanism (max 7 retries)
    attempt = 0
    while attempt < max_tries:
        try:
            categories_df = categorize_transactions(transaction_names, llm)
            
            categories_data.append(categories_df)
            
            break
        except Exception as e:
            attempt += 1
            if attempt == max_tries:
                raise Exception(f"Failed to categorize transactions for index range {i} to {i + 1} after {max_tries} attempts. Error: {e}")

categories_df_all = pd.concat(categories_data, ignore_index=True)

#%%
categories_df_all = categories_df_all.dropna()

categories_df_all.loc[categories_df_all['Category'].str.contains("Food|Snacks"), 'Category'] = "Food and Drinks"
categories_df_all.loc[categories_df_all['Category'].str.contains("Fashion|Shopping|Online shopping"), 'Category'] = "Shopping"
categories_df_all.loc[categories_df_all['Category'].str.contains("Services"), 'Category'] = "Services"
categories_df_all.loc[categories_df_all['Category'].str.contains("Health|Wellness"), 'Category'] = "Health and Wellness"
categories_df_all.loc[categories_df_all['Category'].str.contains("Sport"), 'Category'] = "Sport and Fitness"
categories_df_all.loc[categories_df_all['Category'].str.contains("Travel|Transportation"), 'Category'] = "Travel"

categories_df_all
#%%
categories_df_all['Transaction'] = categories_df_all['Transaction'].str.replace(r'\d+\.\s+', '')
categories_df_all


#%%

from fuzzywuzzy import process

def fuzzy_match(value, choices, threshold=80):
    match, score = process.extractOne(value, choices)
    if score >= threshold:
        return match
    return None

unique_transactions = categories_df_all['Transaction'].unique()

df['Fuzzy_Match_Description'] = df['Description'].apply(lambda x: fuzzy_match(x, unique_transactions))

df_merged = pd.merge(df, categories_df_all, left_on='Fuzzy_Match_Description', right_on='Transaction', how='left')

df_merged = df_merged.drop(columns=['Fuzzy_Match_Description'])

#%%
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')

category_amounts = df_merged.groupby('Category')['Amount'].sum()

plt.figure(figsize=(8, 8))

def autopct_func(pct, allvalues):
    absolute = round(pct / 100.*sum(allvalues), 2)
    return f'{pct:.2f}%\n${absolute:.2f}'

plt.pie(category_amounts, labels=category_amounts.index, autopct=lambda pct: autopct_func(pct, category_amounts),
        startangle=120, colors=plt.cm.Paired.colors, textprops={'color': 'white'}) 

# Title with added padding
plt.title('Spending Distribution by Category', color='white', fontsize=16, pad=20)  

plt.axis('equal') 

plt.show()

category_amounts


