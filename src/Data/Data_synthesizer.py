import os
import requests
import pandas as pd
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict, List

# -----------------------------
# Configuration & Environment
# -----------------------------
CENSUS_API_KEY = 'b9b3ecac3f95ad013778c6ca8f6854480be8f7c0'
DEEPSEEK_API_KEY = 'sk-20f42785068042f1b9d02719d2e22fc6'
API_ENDPOINTS = {
    "census": "https://api.census.gov/data/2023/acs/acs5",
    "deepseek": "https://api.deepseek.com/v1/chat/completions"
}


# -----------------------------
# 1. Enhanced Census Data Fetching
# -----------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_acs_data() -> pd.DataFrame:
    """Fetch ACS data with error handling and retry logic."""
    params = {
        "get": "NAME,B01001_001E,B19013_001E",
        "for": "state:11",
        "key": CENSUS_API_KEY
    }

    try:
        response = requests.get(API_ENDPOINTS["census"], params=params)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0]).apply(pd.to_numeric, errors='ignore')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ACS data: {str(e)}")
        raise


# -----------------------------
# 2. Optimized Customer Generation
# -----------------------------
def generate_synthetic_customers(num_customers: int, acs_df: pd.DataFrame) -> pd.DataFrame:
    """Generate customers using vectorized operations for better performance."""
    acs_df = acs_df.copy()
    acs_df['B19013_001E'] = pd.to_numeric(acs_df['B19013_001E'], errors='coerce')
    avg_income = acs_df['B19013_001E'].mean()

    # Vectorized generation
    data = {
        "Customer_ID": [f"CUST{i:06}" for i in range(1, num_customers + 1)],
        "Age": np.random.randint(18, 81, num_customers),
        "Income": np.maximum(
            np.random.lognormal(mean=np.log(avg_income), sigma=0.3, size=num_customers),
            10000
        ).round(2),
        "Gender": np.random.choice(
            ["Male", "Female", "Other"],
            size=num_customers,
            p=[0.48, 0.48, 0.04]
        ),
        "Location": np.random.choice(
            acs_df['NAME'],
            size=num_customers,
            p=acs_df['B01001_001E'] / acs_df['B01001_001E'].sum()
        )
    }

    return pd.DataFrame(data)


# -----------------------------
# 3. Efficient Transaction Generation
# -----------------------------
def generate_synthetic_transactions(customers_df: pd.DataFrame, num_transactions: int) -> pd.DataFrame:
    """Generate transactions using vectorized operations and proper sampling."""
    # Precompute customer weights based on income
    customer_weights = customers_df["Income"].values
    customer_weights = customer_weights / customer_weights.sum()

    # Sample customers with income-based weighting
    sampled_customers = customers_df.sample(
        n=num_transactions,
        replace=True,
        weights=customer_weights,
        random_state=42
    ).reset_index(drop=True)

    # Generate transaction data
    transactions = {
        "Transaction_ID": [f"TXN{i:06}" for i in range(1, num_transactions + 1)],
        "Customer_ID": sampled_customers["Customer_ID"],
        "Date": pd.to_datetime("now") - pd.to_timedelta(
            np.random.randint(0, 365, num_transactions),
            unit='d'
        ),
        "Amount": np.round(
            np.random.lognormal(
                mean=3,  # Results in typical amounts around $20-30
                sigma=0.5,
                size=num_transactions
            ),
            2
        ),
        "Transaction_Type": np.random.choice(
            ["Debit", "Credit"],
            size=num_transactions,
            p=[0.9, 0.1]
        ),
        "Merchant": np.random.choice(
            ["Starbucks", "Walmart", "Amazon", "Uber", "McDonald's"],
            size=num_transactions,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        ),
        "Category": np.random.choice(
            ["Food & Beverage", "Groceries", "Shopping", "Transportation", "Entertainment"],
            size=num_transactions
        )
    }

    df = pd.DataFrame(transactions)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Description"] = df["Merchant"] + " purchase"  # Temporary placeholder
    return df


# -----------------------------
# 4. DeepSeek API Integration with Parallel Processing
# -----------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_description_parallel(args: Tuple[str, str]) -> str:
    """Generate description using DeepSeek API with parallel processing."""
    merchant, category = args
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": f"Generate a realistic bank statement description for a {category} purchase at {merchant}. Keep it under 10 words."
        }],
        "temperature": 0.7,
        "max_tokens": 25
    }

    try:
        response = requests.post(API_ENDPOINTS["deepseek"], json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return f"{merchant} purchase"


def update_transaction_descriptions(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Batch update descriptions using parallel processing."""
    # Convert to hashable tuples instead of records
    unique_combinations = transactions_df[["Merchant", "Category"]].drop_duplicates()
    args_list = [tuple(row) for row in unique_combinations.values]

    # Generate descriptions in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(generate_description_parallel, args_list))

    # Create mapping and update descriptions
    description_map = {args: result for args, result in zip(args_list, results)}
    transactions_df["Description"] = transactions_df.apply(
        lambda row: description_map.get(
            (row["Merchant"], row["Category"]),
            f"{row['Merchant']} purchase"
        ),
        axis=1
    )
    return transactions_df


# -----------------------------
# 5. Main Execution with Validation
# -----------------------------
if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Fetch and validate ACS data
    try:
        acs_df = fetch_acs_data()
        print("ACS Data Sample:")
        print(acs_df.head())
    except Exception as e:
        print(f"Fatal error fetching data: {str(e)}")
        exit(1)

    # Generate synthetic data
    customers_df = generate_synthetic_customers(1000, acs_df)
    transactions_df = generate_synthetic_transactions(customers_df, 5000)

    # Update descriptions
    try:
        transactions_df = update_transaction_descriptions(transactions_df)
        print("\nTransaction Sample with Enhanced Descriptions:")
        print(transactions_df.sample(5))
    except Exception as e:
        print(f"Error updating descriptions: {str(e)}")
        transactions_df["Description"] = transactions_df["Merchant"] + " purchase"

    # Save results
    customers_df.to_csv("synthetic_customers.csv", index=False)
    transactions_df.to_csv("synthetic_transactions.csv", index=False)