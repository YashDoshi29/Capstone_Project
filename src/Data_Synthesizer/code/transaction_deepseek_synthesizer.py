import pandas as pd
import numpy as np
import random
import requests
import json
import time
from typing import Dict, List
from geopy.distance import geodesic
from config import API_KEY

# Merchant category mapping
CATEGORY_MAPPING = {
    "Grocery Store": "groceries",
    "Restaurant": "dining",
    "Caterers": "dining",
    "Delicatessen": "groceries",
    "Bakery": "groceries",
    "Food Products": "groceries",
    "Gasoline Dealer": "transportation",
    "Auto Rental": "transportation",
    "Auto Wash": "transportation",
    "Motion Picture Theatre": "entertainment",
    "Public Hall": "entertainment",
    "Theater (Live)": "entertainment",
    "Bowling Alley": "entertainment",
    "Hotel": "housing",
    "Inn And Motel": "housing",
    "Vacation Rental": "housing",
    "Beauty Shop": "personal_care",
    "Health Spa": "personal_care",
    "Massage Establishment": "personal_care"
}

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
    def __init__(self, api_key: str):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.spending_categories = {
            'groceries': 0.18,
            'dining': 0.12,
            'transportation': 0.15,
            'housing': 0.25,
            'entertainment': 0.10,
            'personal_care': 0.08,
            'other': 0.12
        }
        self.merchant_cache = {}

    def load_data(self, customers_path: str, merchants_path: str):
        """Load and preprocess input data"""
        self.customers = pd.read_csv(customers_path)
        self.merchants = pd.read_csv(merchants_path)
        self._preprocess_merchants()

    def _preprocess_merchants(self):
        """Organize merchants with proper column names"""
        column_map = {
            'ENTITY_NAME': 'Name',
            'LICENSECATEGORY': 'Category',
            'ZIP': 'Zipcode',
            'LATITUDE': 'Latitude',
            'LONGITUDE': 'Longitude'
        }
        self.merchants = self.merchants.rename(
            columns={k: v for k, v in column_map.items() if k in self.merchants.columns}
        )

        required_cols = ['Name', 'Category', 'Zipcode']
        for col in required_cols:
            if col not in self.merchants.columns:
                raise ValueError(f"Missing required column: {col}")

        # Set default coordinates if missing
        if 'Latitude' not in self.merchants.columns:
            self.merchants['Latitude'] = 38.9072
        if 'Longitude' not in self.merchants.columns:
            self.merchants['Longitude'] = -77.0369

        # Map categories and clean data
        self.merchants['mapped_category'] = self.merchants['Category'].map(CATEGORY_MAPPING)
        self.merchants = self.merchants.dropna(subset=['mapped_category', 'Zipcode'])

        # Clean zipcodes
        self.merchants['Zipcode'] = (
            self.merchants['Zipcode']
            .astype(str)
            .str.extract(r'(\d{5})')[0]
            .fillna('20001')
        )

        # Use include_groups=False to silence the deprecation warning
        self.merchant_cache = (
            self.merchants.groupby(['Zipcode', 'mapped_category'], group_keys=False)
            .apply(lambda x: x.to_dict('records'))
            .to_dict()
        )

    def _get_nearby_merchants(self, base_zip: str, max_distance: int = 2) -> List[Dict]:
        """Find nearby merchants within radius using zipcode coordinates"""
        clean_zip = str(int(float(base_zip))) if base_zip.replace('.', '').isdigit() else '20001'
        clean_zip = clean_zip[:5]

        base_coord = DC_ZIP_COORDS.get(clean_zip, DC_ZIP_COORDS['20001'])

        self.merchants['distance'] = self.merchants.apply(
            lambda row: geodesic(base_coord, (row['Latitude'], row['Longitude'])).miles,
            axis=1
        )
        return self.merchants[self.merchants['distance'] <= max_distance]

    def _get_merchant(self, category: str, zipcode) -> Dict:
        """Find matching merchant with DC-specific fallbacks."""
        # if zipcode is NaN or None, use a fallback
        if pd.isna(zipcode):
            clean_zip = '20001'
        else:
            # convert to string
            zipcode_str = str(zipcode)

            # strip to just digits if it's something like 20001.0
            zipcode_str = zipcode_str.split('.')[0] if '.' in zipcode_str else zipcode_str

            # now check if it's numeric; fallback if not
            if zipcode_str.isdigit():
                clean_zip = zipcode_str[:5]
            else:
                clean_zip = '20001'

        merchants = self.merchant_cache.get((clean_zip, category), [])

        if not merchants:
            nearby_merchants = self._get_nearby_merchants(clean_zip)
            merchants = nearby_merchants[nearby_merchants['mapped_category'] == category].to_dict('records')

        if not merchants:
            # fallback
            fallback_coords = DC_ZIP_COORDS.get(clean_zip, DC_ZIP_COORDS['20001'])
            return {
                "Name": f"DC {category.capitalize()} Service",
                "Category": category,
                "Zipcode": clean_zip,
                "Latitude": fallback_coords[0],
                "Longitude": fallback_coords[1],
                "mapped_category": category
            }

        return random.choice(merchants)

    def _generate_spending_pattern(self, customer: Dict) -> Dict:
        zipcode_str = str(int(customer['zipcode'])) if not pd.isna(customer['zipcode']) else '20000'
        base_allocation = {
            'groceries': 0.18 + (0.02 if customer['household_size'] > 2 else 0),
            'dining': 0.12 + (0.03 if customer['income'] > 75000 else 0),
            'transportation': 0.15 - (0.02 if zipcode_str.startswith('200') else 0),
            'housing': max(0.25, 0.35 - (0.02 * customer['household_size'])),
            'entertainment': 0.10 + (0.02 if customer['age'] < 35 else 0),
            'personal_care': 0.08 + (0.01 * (customer['age'] // 30)),
            'other': 0.12
        }
        return {k: v * customer['income'] / 12 for k, v in base_allocation.items()}

    def _generate_transactions_api(self, customer: Dict, merchant: Dict) -> Dict:
        """Generate transaction using DeepSeek API (no fallback)"""
        prompt = f"""Generate realistic transaction details for a DC resident:
        - Customer Profile: {customer['age']} year old {customer['gender']}, 
          Household size: {customer['household_size']}, 
          Annual income: ${customer['income']:,}
        - Merchant: {merchant['Name']} ({merchant['Category']})
        - Location: {merchant.get('SITE_ADDRESS', merchant['Zipcode'])}
        - Spending Category: {merchant['mapped_category']}
        - Expected spending range: ${self.spending_categories[merchant['mapped_category']] * customer['income'] / 12:,.2f} monthly

        Generate exactly one transaction with these specifications:
        - Amount should be realistic for DC prices
        - Timestamp within last 30 days
        - Appropriate payment method
        - Must include exact field names below

        Required JSON format:
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

        try:
            # Increase the timeout to 60 seconds:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial data expert. Generate ONLY valid JSON output matching the exact specification."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                },
                timeout=60  # <-- Increased timeout
            )
            response.raise_for_status()

            # Parse and validate response
            transaction = json.loads(response.json()['choices'][0]['message']['content'])

            if not all(k in transaction for k in ['amount', 'timestamp', 'merchant_details', 'payment_type']):
                raise ValueError("API response missing required fields")

            return {
                "customer_id": customer['customer_id'],
                "amount": round(float(transaction['amount']), 2),
                "timestamp": transaction['timestamp'],
                "merchant_details": {
                    "name": str(transaction['merchant_details']['name']),
                    "category": str(transaction['merchant_details']['category']),
                    "zipcode": str(transaction['merchant_details']['zipcode'])
                },
                "payment_type": str(transaction['payment_type'])
            }

        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {str(e)}")
            raise
        except json.JSONDecodeError:
            print("API returned invalid JSON")
            raise
        except KeyError as e:
            print(f"API response missing expected field: {str(e)}")
            raise
        except ValueError as e:
            print(f"Data validation error: {str(e)}")
            raise

    def generate_transactions(self, output_path: str):
        """Main transaction generation workflow"""
        transactions = []
        for _, customer in self.customers.iterrows():
            spending = self._generate_spending_pattern(customer.to_dict())

            for category, amount in spending.items():
                merchant = self._get_merchant(category, customer['zipcode'])
                transaction = self._generate_transactions_api(customer.to_dict(), merchant)
                transactions.append(transaction)

                time.sleep(0.5)  # simple rate limiting

        pd.DataFrame(transactions).to_csv(output_path, index=False)
        print(f"Generated {len(transactions)} DC-specific transactions")


# Usage
if __name__ == "__main__":
    generator = TransactionGenerator(api_key=API_KEY)
    generator.load_data(
        customers_path="../data/synthetic_customers_deepseek.csv",
        merchants_path="../data/dc_businesses_cleaned.csv"
    )
    generator.generate_transactions("synthetic_transactions.csv")
