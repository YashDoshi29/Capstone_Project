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

path = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(path, "..", "data", "dc_businesses_cleaned.csv")


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

        # Transaction scaling parameters
        self.MIN_TRANSACTIONS = 5
        self.MAX_TRANSACTIONS = 20
        self.BASE_INCOME = 50000  # Median income for scaling

    def _preprocess_merchants(self):
        """Clean and prepare merchant data"""
        column_map = {
            'ENTITY_NAME': 'Name',
            'LICENSECATEGORY': 'Category',
            'ZIP': 'Zipcode',
            'LATITUDE': 'Latitude',
            'LONGITUDE': 'Longitude'
        }
        self.merchants = self.merchants.rename(columns=column_map)

        # Set default coordinates if missing
        if 'Latitude' not in self.merchants.columns:
            self.merchants['Latitude'] = 38.9072
        if 'Longitude' not in self.merchants.columns:
            self.merchants['Longitude'] = -77.0369

        # Map categories and clean data
        self.merchants['mapped_category'] = (
            self.merchants['Category']
            .map(CATEGORY_MAPPING)
            .fillna('other')
        )
        self.merchants['Zipcode'] = (
            self.merchants['Zipcode']
            .astype(str)
            .str.extract(r'(\d{5})')[0]
            .fillna('20001')
        )

    def _build_merchant_cache(self):
        """Build merchant lookup cache"""
        self.merchant_cache = (
            self.merchants.groupby(['Zipcode', 'mapped_category'])
            .apply(lambda x: x.to_dict('records'))
            .to_dict()
        )

    def _calculate_transaction_count(self, income: float) -> int:
        """Logarithmic scaling of transaction count with income"""
        income_ratio = np.log1p(max(income, 10000) / self.BASE_INCOME)
        scaled = self.MIN_TRANSACTIONS + (self.MAX_TRANSACTIONS - self.MIN_TRANSACTIONS) * income_ratio
        return min(self.MAX_TRANSACTIONS, int(scaled))

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
        clean_zip = zipcode[:5] if zipcode[:5] in DC_ZIP_COORDS else '20001'
        merchants = self.merchant_cache.get((clean_zip, category), [])

        if not merchants:
            nearby_merchants = self._get_nearby_merchants(clean_zip)
            merchants = [
                m for m in nearby_merchants
                if m.get('mapped_category') == category
            ]

        if not merchants:
            # Fallback merchant
            return {
                "Name": f"DC {category.replace('_', ' ').title()}",
                "Category": category,
                "Zipcode": clean_zip,
                "Latitude": DC_ZIP_COORDS[clean_zip][0],
                "Longitude": DC_ZIP_COORDS[clean_zip][1]
            }
        return random.choice(merchants)

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

    def generate_transactions(self, user_data: dict) -> list:
        """Main generation method for React interface"""
        max_retries = 3
        retry_delay = 5

        # Validate input first (outside retry loop)
        required = ['age', 'gender', 'household_size', 'income', 'zipcode']
        if any(field not in user_data for field in required):
            raise ValueError("Missing required user data fields")

        # Create customer profile
        customer = {
            'customer_id': f"WEB-{random.randint(100000, 999999)}",
            **{k: user_data[k] for k in required},
            'zipcode': str(user_data['zipcode'])[:5]
        }

        for attempt in range(max_retries):
            try:
                # Determine transaction count
                tx_count = self._calculate_transaction_count(float(user_data['income']))

                # Assign categories and spending pattern
                categories = self._assign_categories()
                if not categories:
                    raise ValueError("No spending categories assigned")

                spending_pattern = self._generate_spending_pattern(categories, customer['income'])
                subcats, weights = zip(*spending_pattern.items())
                probs = np.array(weights) / sum(weights)

                transactions = []
                for _ in range(tx_count):
                    try:
                        # Select category and merchant
                        category = np.random.choice(subcats, p=probs)
                        merchant = self._get_merchant(category, customer['zipcode'])

                        if not merchant.get('mapped_category'):
                            merchant['mapped_category'] = category

                        # Generate transaction via API
                        txn = self._generate_transaction(customer, merchant)
                        transactions.append(txn)

                        # Rate limiting
                        time.sleep(1.0)  # More conservative delay for Groq API

                    except Exception as e:
                        print(f"Transaction generation failed: {str(e)}")
                        continue

                return transactions

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    sleep_time = retry_delay * (attempt + 1)
                    print(f"Rate limited, retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                raise

            except Exception as e:
                print(f"Transaction batch failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Max retries exceeded: {str(e)}")
                time.sleep(retry_delay)
                continue

        return []

    def _generate_transaction(self, customer: dict, merchant: dict) -> dict:
        """Call Groq API to generate single transaction with enhanced error handling"""
        try:
            # Ensure required merchant fields exist
            merchant.setdefault('mapped_category', merchant.get('Category', 'other'))
            merchant.setdefault('Name', 'Local Merchant')
            merchant.setdefault('Zipcode', customer['zipcode'])

            prompt = f"""Generate realistic transaction details:
            - Customer: {customer['age']}yo {customer['gender']}, 
              {customer['household_size']} household members
            - Income: ${customer['income']:,}/year
            - Merchant: {merchant['Name']} ({merchant.get('Category', 'retail')})
            - Location: {merchant['Zipcode']}
            - Category: {merchant['mapped_category']}

            Output must be valid JSON with these exact fields:
            {{
                "amount": float,
                "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
                "merchant_details": {{
                    "name": "string",
                    "category": "string",
                    "zipcode": "string"
                }},
                "payment_type": "string"
            }}"""

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial data generator. Output must be valid JSON with exactly the fields specified."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            response.raise_for_status()

            # More robust response parsing
            try:
                content = response.json()['choices'][0]['message']['content']
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                txn = json.loads(content.strip())

                # Validate response structure
                required_fields = ['amount', 'timestamp', 'merchant_details', 'payment_type']
                if not all(field in txn for field in required_fields):
                    raise ValueError("Missing required fields in API response")

                return {
                    "customer_id": customer['customer_id'],
                    "amount": round(float(txn['amount']), 2),
                    "timestamp": txn['timestamp'],
                    "merchant_details": {
                        "name": str(txn['merchant_details']['name']),
                        "category": str(txn['merchant_details']['category']),
                        "zipcode": str(txn['merchant_details']['zipcode'])
                    },
                    "payment_type": str(txn['payment_type'])
                }

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise ValueError(f"Invalid API response format: {str(e)}")

        except Exception as e:
            raise ValueError(f"Transaction generation failed: {str(e)}")


# FastAPI Setup
app = FastAPI()

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


# Initialize generator once at startup
merchants_df = pd.read_csv(df_path)
generator = TransactionGenerator(api_key=API_KEY_Groq, merchants_df=merchants_df)


@app.post("/generate")
async def generate_transactions(user_input: UserInput):
    try:
        transactions = generator.generate_transactions(user_input.dict())
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)