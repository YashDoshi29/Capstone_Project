import requests
import json
from datetime import datetime
import time

def test_transaction_generator(base_url: str = "http://0.0.0.0:8000"):
    """Simple test for transaction generator"""
    
    test_profile = {
        "age": 30,
        "gender": "Female",
        "household_size": 2,
        "income": 75000,
        "zipcode": "20001"
    }
    
    print("\n=== Testing Transaction Generator ===")
    print(f"Testing with profile: {json.dumps(test_profile, indent=2)}")
    
    try:
        start_time = time.time()
        print("\nMaking API request...")
        
        response = requests.post(
            f"{base_url}/generate",
            json=test_profile,
            timeout=120  # Increased timeout for batch processing
        )
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return
        
        data = response.json()
        transactions = data.get("transactions", [])
        
        if not transactions:
            print("❌ No transactions generated")
            return
        
        # Basic validation and stats
        valid_count = 0
        total_amount = 0
        merchants = set()
        categories = set()
        
        print("\nValidating transactions...")
        for tx in transactions:
            try:
                # Basic validation
                if (isinstance(tx, dict) and 
                    isinstance(tx.get('amount'), (int, float)) and
                    isinstance(tx.get('timestamp'), str) and
                    isinstance(tx.get('merchant_details'), dict)):
                    
                    valid_count += 1
                    total_amount += tx['amount']
                    merchants.add(tx['merchant_details'].get('name', ''))
                    categories.add(tx['merchant_details'].get('category', ''))
            except Exception as e:
                print(f"Invalid transaction: {str(e)}")
        
        # Print results
        duration = time.time() - start_time
        print(f"\n=== Results ===")
        print(f"✅ Generated {len(transactions)} transactions in {duration:.1f} seconds")
        print(f"Valid transactions: {valid_count}")
        print(f"Total amount: ${total_amount:.2f}")
        print(f"Average amount: ${total_amount/valid_count:.2f}")
        print(f"Unique merchants: {len(merchants)}")
        print(f"Unique categories: {len(categories)}")
        
        # Show sample transactions
        print("\nSample Transactions (first 2):")
        for tx in transactions[:2]:
            print(f"\nAmount: ${tx['amount']:.2f}")
            print(f"Date: {tx['timestamp']}")
            print(f"Merchant: {tx['merchant_details']['name']}")
            print(f"Category: {tx['merchant_details']['category']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_transaction_generator()
