# main.py
import numpy as np
from census_fetcher import cache_acs_data
from merchant_fetcher import cache_merchant_data
from synthesizer import generate_synthetic_customers, generate_synthetic_transactions
from config import STATES

def main():
    np.random.seed(42)
    state = "DC"  # Change as needed (e.g., "VA")
    acs_variables = ["NAME", "B01001_001E", "B19013_001E"]

    # Fetch and cache ACS data for the selected state.
    try:
        acs_df = cache_acs_data(state, acs_variables)
        print("ACS Data Sample:")
        print(acs_df.head())
    except Exception as e:
        print(f"Fatal error fetching ACS data: {e}")
        return

    # Fetch and cache Merchant data for the selected state.
    merchants_df = cache_merchant_data(state)
    if not merchants_df.empty:
        print("Merchant Data Sample:")
        print(merchants_df.head())
    else:
        print("Using default merchant list as fallback.")

    # Generate synthetic customers and transactions.
    customers_df = generate_synthetic_customers(1000, acs_df)
    transactions_df = generate_synthetic_transactions(customers_df, merchants_df, 5000)

    # Save the results locally.
    customers_df.to_csv("synthetic_customers.csv", index=False)
    transactions_df.to_csv("synthetic_transactions.csv", index=False)
    print("Synthetic data generated and saved.")

if __name__ == "__main__":
    main()
