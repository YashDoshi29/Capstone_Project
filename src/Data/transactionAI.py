# dc_transaction_generator.py
import os
import requests
import pandas as pd
import time

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Set your API key in environment


def generate_dc_transactions(output_file="dc_transactions.csv"):
    """Generate realistic transactions across all DC zipcodes"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = """Generate a CSV of 100,000 credit card transactions for Washington DC residents with columns:
1. transaction_id: Unique ID (TX{10dig})
2. customer_id: CUST{8dig}
3. transaction_date: Dates between 2023-01-01 and 2024-01-01
4. merchant_name: Actual DC businesses across all neighborhoods
5. category: Groceries, Dining, Retail, Services, Transportation, Entertainment
6. amount: Realistic USD values for category
7. zipcode: Valid DC zipcodes (distributed naturally)
8. is_online: 0/1 (15% online transactions)
9. latitude: DC coordinates (38.8XXX-38.9XXX)
10. longitude: DC coordinates (-77.0XXX--77.1XXX)

Requirements:
- Natural geographic distribution across all DC zipcodes
- Category distributions matching urban spending patterns
- Include both chain stores and local businesses
- 5% declined transactions
- Time patterns (more dining at night, groceries on weekends)
- No zipcode-specific hardcoding - let patterns emerge naturally

Output format: CSV with header"""

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 4000,
        "response_format": {"type": "csv"}
    }

    for attempt in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return process_transactions(response.json()['choices'][0]['message']['content'], output_file)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2 ** attempt)

    raise Exception("API request failed after 3 attempts")


def process_transactions(csv_data, output_file):
    """Process and validate transaction data"""
    df = pd.read_csv(pd.compat.StringIO(csv_data))

    # Data cleaning
    df = df.drop_duplicates('transaction_id')
    df['zipcode'] = df['zipcode'].astype(str).str[:5]
    df['amount'] = df['amount'].replace('[\$,]', '', regex=True).astype(float)

    # DC validation
    valid_zips = set([str(z) for z in range(20001, 20099) if z not in [20000, 20020, 20036]])
    df = df[df['zipcode'].isin(valid_zips)]

    # Coordinate validation
    df = df[
        (df['latitude'].between(38.7916, 38.9957)) &
        (df['longitude'].between(-77.1198, -76.9094))
        ]

    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} transactions with {df.zipcode.nunique()} zipcodes")
    return df


if __name__ == "__main__":
    transactions = generate_dc_transactions()

    # Analysis
    print("\nZipcode Distribution:")
    print(transactions['zipcode'].value_counts().head(10))

    print("\nCategory Distribution:")
    print(transactions['category'].value_counts(normalize=True))