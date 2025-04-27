import requests
import json
from datetime import datetime
from collections import Counter

def test_single_customer(base_url: str = "http://0.0.0.0:8000"):
    """Test the transaction generator API with a single customer profile"""
    
    # Single test case representing a typical user
    test_case = {
        "age": 30,
        "gender": "Female",
        "household_size": 2,
        "income": 75000,
        "zipcode": "20001"
    }
    
    print("\n=== Testing Transaction Generator ===")
    print("Customer Profile:")
    for key, value in test_case.items():
        print(f"  {key}: {value}")
    
    try:
        # Make API request
        response = requests.post(f"{base_url}/generate", json=test_case, timeout=60)
        
        if response.status_code != 200:
            print(f"\n❌ API request failed with status code {response.status_code}")
            print(f"Error: {response.text}")
            return
        
        # Process successful response
        data = response.json()
        transactions = data.get("transactions", [])
        
        # Collect unique merchants
        merchants = Counter(tx['merchant_details']['name'] for tx in transactions)
        
        print(f"\n=== Generated {len(transactions)} transactions ===")
        
        print("\nUnique Merchants Used:")
        for merchant, count in merchants.items():
            print(f"  {merchant}: {count} transaction(s)")
        
        print("\nDetailed Transactions:")
        for idx, tx in enumerate(transactions, 1):
            print(f"\nTransaction #{idx}:")
            print(f"  Amount: ${tx['amount']:.2f}")
            print(f"  Date: {tx['timestamp']}")
            print(f"  Merchant: {tx['merchant_details']['name']}")
            print(f"  Category: {tx['merchant_details']['category']}")
            print(f"  Location: {tx['merchant_details']['zipcode']}")
            print(f"  Payment: {tx['payment_type']}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    try:
        test_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY_Groq}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
        )
        if test_response.status_code != 200:
            print(f"API Key test failed: {test_response.status_code}")
            print(test_response.text)
    except Exception as e:
        print(f"API Key test failed: {str(e)}")
    test_single_customer()
