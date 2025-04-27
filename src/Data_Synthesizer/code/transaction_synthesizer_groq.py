import pandas as pd
import numpy as np
import random
import requests
import json
import time
from typing import Dict, List
from geopy.distance import geodesic
from config import API_KEY_Groq
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

path = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(path, "..", "data", "dc_businesses_cleaned.csv")

if not API_KEY_Groq or len(API_KEY_Groq.strip()) < 20:
    raise ValueError("""
    Invalid or missing Groq API key. 
    Make sure your config.py file contains a valid API_KEY_Groq value.
    """)

# Updated Merchant category mapping
CATEGORY_MAPPING = {
    # Food & Grocery
    "Grocery Store": "groceries",
    "Delicatessen": "deli_prepared_foods",
    "Bakery": "bakery",
    "Food Products": "packaged_foods",
    "Food Vending Machine": "vending_snacks",
    "Ice Cream Manufacture": "ice_cream",
    "Marine Food Retail": "seafood_market",
    "Mobile Delicatessen": "food_truck",

    # Dining
    "Restaurant": "restaurant_dining",
    "Caterers": "catering_services",

    # Transportation
    "Gasoline Dealer": "gas_station",
    "Auto Rental": "car_rental",
    "Auto Wash": "car_wash",
    "Tow Truck": "towing_services",
    "Tow Truck Business": "towing_company",
    "Tow Truck Storage Lot": "vehicle_storage",
    "Driving School": "driving_lessons",

    # Entertainment
    "Motion Picture Theatre": "movie_theater",
    "Public Hall": "event_venue",
    "Theater (Live)": "live_theater",
    "Bowling Alley": "bowling",
    "Billiard Parlor": "pool_hall",
    "Skating Rink": "skating_rink",
    "Athletic Exhibition": "sports_events",
    "Special Events": "special_events",

    # Lodging
    "Hotel": "hotel_lodging",
    "Inn And Motel": "motel_lodging",
    "Bed and Breakfast": "bnb_lodging",
    "Vacation Rental": "vacation_rental",
    "Boarding House": "boarding_house",

    # Personal Care
    "Beauty Shop": "beauty_services",
    "Barber Shop": "barber_services",
    "Beauty Booth": "beauty_booth",
    "Beauty Shop Braiding": "hair_braiding",
    "Beauty Shop Electrology": "electrolysis",
    "Beauty Shop Esthetics": "skin_care",
    "Beauty Shop Nails": "nail_salon",
    "Health Spa": "spa_services",
    "Massage Establishment": "massage_parlor",
}

# Approximate coordinates for DC ZIP codes
DC_ZIP_COORDS = {
    '20001': (38.9109, -77.0163),
    '20002': (38.9123, -77.0127),
    '20003': (38.8857, -76.9894),
    '20004': (38.8951, -77.0366),
    '20005': (38.9026, -77.0311),
    '20006': (38.8979, -77.0369),
    '20007': (38.9183, -77.0709),
    '20008': (38.9368, -77.0595),
    '20009': (38.9193, -77.0374),
    '20010': (38.9327, -77.0294),
    '20011': (38.9566, -77.0232),
    '20012': (38.9770, -77.0296),
    '20015': (38.9664, -77.0846),
    '20016': (38.9346, -77.0896),
    '20017': (38.9348, -76.9886),
    '20018': (38.9238, -76.9894),
    '20019': (38.8898, -76.9488),
    '20020': (38.8641, -76.9857),
    '20024': (38.8743, -77.0167),
    '20032': (38.8458, -77.0013),
    '20036': (38.9055, -77.0417),
    '20037': (38.8996, -77.0527),
    '20052': (38.8990, -77.0479),
    '20057': (38.9087, -77.0731),
    '20064': (38.9335, -76.9978),
}


class TransactionGenerator:
    def __init__(self, api_key: str, merchants_df: pd.DataFrame):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.merchants = merchants_df
        self._preprocess_merchants()
        self._build_merchant_cache()

        self.spending_categories = {
            # Food & Grocery
            "groceries": 0.14,
            "deli_prepared_foods": 0.02,
            "bakery": 0.02,
            "packaged_foods": 0.02,
            "vending_snacks": 0.01,
            "ice_cream": 0.01,
            "seafood_market": 0.02,
            "food_truck": 0.02,

            # Dining
            "restaurant_dining": 0.10,
            "catering_services": 0.02,

            # Transportation
            "gas_station": 0.05,
            "car_rental": 0.01,
            "car_wash": 0.01,
            "towing_services": 0.00,
            "towing_company": 0.00,
            "vehicle_storage": 0.00,
            "driving_lessons": 0.01,

            # Entertainment
            "movie_theater": 0.03,
            "event_venue": 0.02,
            "live_theater": 0.01,
            "bowling": 0.01,
            "pool_hall": 0.01,
            "skating_rink": 0.01,
            "sports_events": 0.02,
            "special_events": 0.02,

            # Lodging
            "hotel_lodging": 0.04,
            "motel_lodging": 0.02,
            "bnb_lodging": 0.01,
            "vacation_rental": 0.02,
            "boarding_house": 0.01,

            # Personal Care
            "beauty_services": 0.03,
            "barber_services": 0.02,
            "beauty_booth": 0.00,
            "hair_braiding": 0.00,
            "electrolysis": 0.00,
            "skin_care": 0.01,
            "nail_salon": 0.01,
            "spa_services": 0.02,
            "massage_parlor": 0.01
        }

        # Update transaction scaling parameters for weekly data
        self.MIN_TRANSACTIONS_PER_DAY = 2
        self.MAX_TRANSACTIONS_PER_DAY = 8
        self.BASE_INCOME = 50000

    def _preprocess_merchants(self):
        """Clean and prepare merchant data"""
        try:
            print("\n=== Preprocessing Merchants ===")
            print(f"Initial merchant count: {len(self.merchants)}")
            print("Initial columns:", self.merchants.columns.tolist())

            # Rename columns
            column_map = {
                'ENTITY_NAME': 'Name',
                'LICENSECATEGORY': 'Category',
                'ZIP': 'Zipcode',
                'LATITUDE': 'Latitude',
                'LONGITUDE': 'Longitude'
            }
            self.merchants = self.merchants.rename(columns=column_map)
            print("\nColumns after renaming:", self.merchants.columns.tolist())

            # Set default coordinates
            if 'Latitude' not in self.merchants.columns:
                self.merchants['Latitude'] = 38.9072
                print("Added default Latitude")
            if 'Longitude' not in self.merchants.columns:
                self.merchants['Longitude'] = -77.0369
                print("Added default Longitude")

            # Map categories
            print("\nMapping categories...")
            print("Original categories sample:", self.merchants['Category'].unique()[:5])
            
            self.merchants['mapped_category'] = (
                self.merchants['Category']
                .map(CATEGORY_MAPPING)
                .fillna('other')
            )
            
            print("Mapped categories sample:", self.merchants['mapped_category'].unique()[:5])
            print(f"Total unique mapped categories: {self.merchants['mapped_category'].nunique()}")

            # Clean zipcode
            print("\nCleaning zipcodes...")
            self.merchants['Zipcode'] = (
                self.merchants['Zipcode']
                .astype(str)
                .str.extract(r'(\d{5})')[0]
                .fillna('20001')
            )
            
            print("Sample zipcodes:", self.merchants['Zipcode'].unique()[:5])
            print(f"\nFinal merchant count: {len(self.merchants)}")
            
            # Show sample of processed data
            print("\nSample of processed merchants:")
            print(self.merchants[['Name', 'Category', 'mapped_category', 'Zipcode']].head())

        except Exception as e:
            print(f"Error in preprocessing merchants: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def _build_merchant_cache(self):
        """Build merchant lookup cache"""
        try:
            print("\nBuilding merchant cache...")
            
            # Group by both zipcode and category
            self.merchant_cache = {}
            for zip_code in self.merchants['Zipcode'].unique():
                for category in self.merchants['mapped_category'].unique():
                    merchants = self.merchants[
                        (self.merchants['Zipcode'] == zip_code) & 
                        (self.merchants['mapped_category'] == category)
                    ].to_dict('records')
                    
                    if merchants:
                        self.merchant_cache[(zip_code, category)] = merchants
            
            print(f"Cache built with {len(self.merchant_cache)} zip+category combinations")
            
        except Exception as e:
            print(f"Error building merchant cache: {str(e)}")
            raise

    def _calculate_transaction_count(self, income: float, days: int = 7) -> int:
        """Logarithmic scaling of transaction count with income for multiple days"""
        income_ratio = np.log1p(max(income, 10000) / self.BASE_INCOME)
        daily_min = self.MIN_TRANSACTIONS_PER_DAY
        daily_max = self.MAX_TRANSACTIONS_PER_DAY
        
        daily_scaled = daily_min + (daily_max - daily_min) * income_ratio
        total_transactions = int(daily_scaled * days)
        return total_transactions

    def _get_nearby_merchants(self, base_zip: str, max_distance: int = 2) -> List[Dict]:
        """Find merchants within 'max_distance' miles using geodesic distance."""
        clean_zip = str(int(float(base_zip))) if base_zip.replace('.', '').isdigit() else '20001'
        clean_zip = clean_zip[:5]
        base_coord = DC_ZIP_COORDS.get(clean_zip, DC_ZIP_COORDS['20001'])

        self.merchants['distance'] = self.merchants.apply(
            lambda row: geodesic(base_coord, (row['Latitude'], row['Longitude'])).miles,
            axis=1
        )
        return self.merchants[self.merchants['distance'] <= max_distance]

    def _get_merchant(self, category: str, zipcode: str) -> dict:
        """Find appropriate merchant with fallback"""
        try:
            clean_zip = zipcode[:5] if zipcode[:5] in DC_ZIP_COORDS else '20001'
            
            # Debug print
            print(f"\nLooking for merchant in category: {category} for zipcode: {clean_zip}")
            
            # First try exact match from cache
            cache_key = (clean_zip, category)
            cached_merchants = self.merchant_cache.get(cache_key, [])
            
            if cached_merchants:
                print(f"Found {len(cached_merchants)} merchants in cache for {category}")
                return random.choice(cached_merchants)

            # If no exact match, try nearby merchants
            print("No cached merchants found, searching nearby...")
            nearby_merchants = self._get_nearby_merchants(clean_zip)
            
            # Filter for matching category
            matching_merchants = nearby_merchants[
                nearby_merchants['mapped_category'] == category
            ].to_dict('records')
            
            if matching_merchants:
                print(f"Found {len(matching_merchants)} nearby merchants for {category}")
                return random.choice(matching_merchants)

            # Fallback only if no real merchants found
            print(f"No merchants found for {category}, using fallback")
            return {
                "Name": f"DC {category.replace('_', ' ').title()}",
                "Category": category,
                "Zipcode": clean_zip,
                "Latitude": DC_ZIP_COORDS[clean_zip][0],
                "Longitude": DC_ZIP_COORDS[clean_zip][1]
            }
        except Exception as e:
            print(f"Error in _get_merchant: {str(e)}")
            raise

    def _assign_categories(self) -> list:
        """Random category assignment with income weighting"""
        base_prob = 0.7  # Base probability for essential categories
        return [
            cat for cat, prob in self.spending_categories.items()
            if random.random() < base_prob + (prob * 0.3)
        ]

    def _generate_spending_pattern(self, categories: list, income: float) -> dict:
        """Create spending distribution based on categories and income"""
        monthly_income = income / 12
        total_weight = sum(self.spending_categories[cat] for cat in categories)

        return {
            cat: (self.spending_categories[cat] / total_weight) * monthly_income
            for cat in categories
        }

    def _batch_generate_transactions(self, customer: dict, merchants: list, num_tx: int) -> List[dict]:
        """Generate multiple transactions in a single API call"""
        try:
            print("\nPreparing to generate transactions...")
            
            # Prepare a simpler list of merchants for the prompt
            merchant_examples = []
            for m in merchants[:10]:  # Limit to 10 merchants to keep prompt size reasonable
                name = m.get('Name', '')
                category = m.get('Category', '')
                if name and category:
                    merchant_examples.append(f"{name} ({category})")

            # Simplified prompt
            prompt = f"""Create {num_tx} transactions using these real DC merchants:

Available DC Merchants:
{chr(10).join('- ' + m for m in merchant_examples)}

Customer: {customer['age']} year old {customer['gender']}, income ${customer['income']}/year

Generate a JSON array of transactions. Each transaction must use one of the merchants listed above.
Example format:
[
    {{
        "amount": 45.99,
        "timestamp": "2024-03-22T14:30:00Z",
        "merchant_details": {{
            "name": "{merchant_examples[0].split('(')[0].strip()}",
            "category": "{merchants[0].get('Category', '')}",
            "zipcode": "{customer['zipcode']}"
        }},
        "payment_type": "credit_card"
    }}
]"""

            print("Making API request...")
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a transaction generator. Generate only valid JSON arrays of transactions."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60
            )

            print(f"API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API Error: {response.text}")
                return []

            # Parse response
            try:
                response_data = response.json()
                print("Successfully got JSON response from API")
                
                # Extract the content from the nested response
                content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                if not content:
                    print("No content in API response")
                    return []

                # Clean up the content - remove any text before the JSON array
                content = content.strip()
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx == -1 or end_idx == 0:
                    print("Could not find JSON array in content")
                    return []
                
                json_content = content[start_idx:end_idx]
                
                # Parse the JSON array
                transactions = json.loads(json_content)
                if not isinstance(transactions, list):
                    print(f"Expected list but got {type(transactions)}")
                    return []

                print(f"Successfully parsed {len(transactions)} transactions")

                # Create merchant lookup for validation
                merchant_lookup = {m.get('Name', ''): m for m in merchants}

                # Process transactions
                processed_transactions = []
                for idx, txn in enumerate(transactions):
                    try:
                        merchant_name = txn.get('merchant_details', {}).get('name', '').strip()
                        merchant = merchant_lookup.get(merchant_name)
                        
                        if not merchant:
                            print(f"Warning: Merchant not found: {merchant_name}")
                            # Use the merchant details as provided in the response
                            merchant = txn.get('merchant_details', {})
                        
                        processed_txn = {
                            "customer_id": customer["customer_id"],
                            "amount": round(float(txn.get("amount", 0)), 2),
                            "timestamp": txn.get("timestamp", ""),
                            "merchant_details": {
                                "name": merchant_name,
                                "category": merchant.get('category', txn.get('merchant_details', {}).get('category', '')),
                                "zipcode": merchant.get('zipcode', txn.get('merchant_details', {}).get('zipcode', customer['zipcode']))
                            },
                            "payment_type": txn.get("payment_type", "credit_card")
                        }

                        if processed_txn["amount"] > 0 and processed_txn["timestamp"]:
                            processed_transactions.append(processed_txn)
                            print(f"Processed transaction {idx + 1}: {merchant_name} - ${processed_txn['amount']}")

                    except Exception as e:
                        print(f"Error processing transaction {idx + 1}: {str(e)}")
                        continue

                print(f"Successfully processed {len(processed_transactions)} transactions")
                return processed_transactions

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print("Raw response:", response.text[:500])  # Print first 500 chars
                return []
            except Exception as e:
                print(f"Error processing API response: {str(e)}")
                return []

        except Exception as e:
            print(f"Batch generation failed: {str(e)}")
            return []

    def generate_transactions(self, user_data: dict) -> list:
        """Main generation method"""
        try:
            print("\n=== Starting Transaction Generation ===")
            print(f"User data: {user_data}")

            # Validate input
            required = ['age', 'gender', 'household_size', 'income', 'zipcode']
            if any(field not in user_data for field in required):
                raise ValueError("Missing required user data fields")

            # Create customer profile
            customer = {
                'customer_id': f"WEB-{random.randint(100000, 999999)}",
                **{k: str(user_data[k]) if k == 'zipcode' else user_data[k] for k in required}
            }
            print(f"\nCustomer profile created: {customer}")

            # Calculate number of transactions
            income = float(user_data['income'])
            tx_count = max(5, min(20, int(np.log1p(income/50000) * 10)))
            print(f"\nCalculated transaction count: {tx_count}")

            # Get categories
            categories = self._assign_categories()
            print(f"\nAssigned categories: {categories}")
            if not categories:
                raise ValueError("No categories assigned")

            # Debug merchant cache
            print("\nMerchant cache status:")
            print(f"Total cached combinations: {len(self.merchant_cache)}")
            sample_key = next(iter(self.merchant_cache)) if self.merchant_cache else None
            if sample_key:
                print(f"Sample cache key: {sample_key}")
                print(f"Sample merchants for key: {len(self.merchant_cache[sample_key])}")

            # Get merchants
            merchants = []
            print("\nFetching merchants for each category:")
            for cat in categories:
                try:
                    merchant = self._get_merchant(cat, customer['zipcode'])
                    if merchant:
                        print(f"✓ Found merchant for {cat}: {merchant.get('Name', 'Unknown')}")
                        merchants.append(merchant)
                    else:
                        print(f"✗ No merchant found for {cat}")
                except Exception as e:
                    print(f"✗ Error getting merchant for {cat}: {str(e)}")

            merchants = [m for m in merchants if m]
            print(f"\nTotal valid merchants found: {len(merchants)}")
            
            if not merchants:
                raise ValueError("No valid merchants available")

            # Show sample merchants
            print("\nSample merchants to be used:")
            for idx, m in enumerate(merchants[:5]):
                print(f"{idx + 1}. {m.get('Name', 'Unknown')} - {m.get('Category', 'Unknown')}")

            # Generate transactions
            print(f"\nGenerating {tx_count} transactions...")
            transactions = self._batch_generate_transactions(customer, merchants, tx_count)
            
            if not transactions:
                print("❌ No transactions were generated by batch generator")
                raise ValueError("No transactions generated")

            print(f"\n✅ Successfully generated {len(transactions)} transactions")
            return transactions

        except Exception as e:
            print(f"\n❌ Transaction generation failed: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise


# First load the raw data
print("\n=== Loading Merchant Data ===")
print(f"CSV Path: {df_path}")
print(f"CSV exists: {os.path.exists(df_path)}")
if os.path.exists(df_path):
    print(f"CSV size: {os.path.getsize(df_path)} bytes")
    print("First few rows:")
    merchants_df_raw = pd.read_csv(df_path)
    print(merchants_df_raw.head())
else:
    raise FileNotFoundError(f"Merchant data file not found: {df_path}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("\n=== Raw Merchant Data Information ===")
    print(f"Total merchants loaded: {len(merchants_df_raw)}")
    print("\nSample merchants (raw data):")
    print(merchants_df_raw[['Name', 'Category', 'Zipcode']].head())
    print("\nUnique categories:", merchants_df_raw['Category'].nunique())
    
    yield
    
    # Shutdown
    print("\nShutting down application...")

# Update FastAPI initialization
app = FastAPI(lifespan=lifespan)

# Allow frontend to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    age: int
    gender: str
    household_size: int
    income: float
    zipcode: str


# Initialize generator with processed data
generator = TransactionGenerator(api_key=API_KEY_Groq, merchants_df=merchants_df_raw)


@app.post("/generate")
async def generate_transactions(user_in: UserInput):
    try:
        print("\n=== New Transaction Request ===")
        print(f"Input data: {user_in.model_dump()}")
        
        data = user_in.model_dump()
        tx = generator.generate_transactions(data)
        
        if not tx:
            error_msg = "No transactions were generated"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        print(f"✅ Successfully generated {len(tx)} transactions")
        return {"transactions": tx}
        
    except ValueError as ve:
        error_msg = f"Validation error: {str(ve)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)