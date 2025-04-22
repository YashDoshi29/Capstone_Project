import pandas as pd
import numpy as np
import random
import requests
import json
import time
from typing import Dict, List
from geopy.distance import geodesic
from config import API_KEY_Groq

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
    def __init__(self, api_key: str):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # More granular spending categories based on your new subcategories
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

        self.merchant_cache = {}
        self.target_transactions = 1000  # We want to end up with 10k total

    def load_data(self, customers_path: str, merchants_path: str):
        """
        Load and preprocess input data. Then randomly pick customers from a large dataset.
        """
        all_customers = pd.read_csv(customers_path)
        # Randomly pick 150 from the dataset
        self.customers = all_customers.sample(n=25, random_state=42).reset_index(drop=True)

        self.merchants = pd.read_csv(merchants_path)
        self._preprocess_merchants()

    def _preprocess_merchants(self):
        """Organize merchants with proper column names and map to subcategories."""
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

        # Map categories and remove rows that don't match our subcategory mapping
        self.merchants['mapped_category'] = self.merchants['Category'].map(CATEGORY_MAPPING)
        self.merchants = self.merchants.dropna(subset=['mapped_category', 'Zipcode'])

        # Clean zipcodes
        self.merchants['Zipcode'] = (
            self.merchants['Zipcode']
            .astype(str)
            .str.extract(r'(\d{5})')[0]
            .fillna('20001')
        )

        self.merchant_cache = (
            self.merchants.groupby(['Zipcode', 'mapped_category'], group_keys=False)
            .apply(lambda x: x.to_dict('records'))
            .to_dict()
        )

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

    def _get_merchant(self, category: str, zipcode) -> Dict:
        """Find a merchant in the same or nearby zip; fallback if none found."""
        if pd.isna(zipcode):
            clean_zip = '20001'
        else:
            zipcode_str = str(zipcode).split('.')[0] if '.' in str(zipcode) else str(zipcode)
            clean_zip = zipcode_str[:5] if zipcode_str.isdigit() else '20001'

        merchants = self.merchant_cache.get((clean_zip, category), [])

        if not merchants:
            # Attempt nearby
            nearby_merchants = self._get_nearby_merchants(clean_zip)
            merchants = nearby_merchants[nearby_merchants['mapped_category'] == category].to_dict('records')

        if not merchants:
            # fallback merchant
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

    def _assign_categories_for_user(self) -> List[str]:
        """
        Decide which subcategories a user actually uses.
        For example, 70-80% chance for popular categories, lower for niche ones.
        You can set your own logic or random approach.
        """
        chosen = []
        for subcat in self.spending_categories.keys():
            # A small chance to skip each category
            # e.g. maybe 70% chance user actually uses "groceries", 10% chance for "car_wash," etc.
            # We'll do a simpler approach: if random() < 0.7, they use it, else skip
            # You can refine this by subcat importance
            if random.random() < 0.7:
                chosen.append(subcat)
        return chosen

    def _generate_spending_pattern(self, user_subcats: List[str], customer: Dict) -> Dict:
        """
        Build a dictionary { subcat: monthly_spend_estimate } for subcats the user has.
        We'll scale by the user's income to get approximate monthly spending.
        """
        monthly_income = customer['income'] / 12.0
        # We sum up all subcategory base percentages for the subcats the user actually uses
        total_base = sum(self.spending_categories[subcat] for subcat in user_subcats if subcat in self.spending_categories)

        # Build a normalized distribution across their chosen subcats
        pattern = {}
        for subcat in user_subcats:
            base_p = self.spending_categories.get(subcat, 0.0)
            if total_base > 0:
                fraction = base_p / total_base
            else:
                fraction = 0.0
            # approximate monthly spend
            pattern[subcat] = fraction * monthly_income

        return pattern

    def _generate_transactions_api(self, customer: Dict, merchant: Dict) -> Dict:
        """Generate a single transaction via the Groq Chat Completion API."""
        # Use the subcategory's base percentage for context in the prompt
        expected_monthly = self.spending_categories.get(merchant['mapped_category'], 0.05) * customer['income'] / 12

        prompt = f"""Generate realistic transaction details for a DC resident:
        - Customer Profile: {customer['age']} year old {customer['gender']},
          Household size: {customer['household_size']},
          Annual income: ${customer['income']:,}
        - Merchant: {merchant['Name']} ({merchant['Category']})
        - Location: {merchant.get('SITE_ADDRESS', merchant['Zipcode'])}
        - Spending Category: {merchant['mapped_category']}
        - Expected spending range: ${expected_monthly:,.2f} monthly

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
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial data expert. Output valid JSON only, no code fences."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "max_tokens": 500
                },
                timeout=60
            )
            response.raise_for_status()

            raw_api_response = response.json()
            if "choices" not in raw_api_response or not raw_api_response["choices"]:
                raise ValueError(f"No valid choices in response: {raw_api_response}")

            content = raw_api_response["choices"][0]["message"]["content"]
            # Remove code fences if present
            if content.startswith("```"):
                content = content.split('\n', 1)[1]
                if "```" in content:
                    content = content.rsplit("```", 1)[0]

            transaction_json = json.loads(content)

            if not all(k in transaction_json for k in ["amount", "timestamp", "merchant_details", "payment_type"]):
                raise ValueError("API response missing required fields")

            return {
                "customer_id": customer["customer_id"],
                "amount": round(float(transaction_json["amount"]), 2),
                "timestamp": transaction_json["timestamp"],
                "merchant_details": {
                    "name": str(transaction_json["merchant_details"]["name"]),
                    "category": str(transaction_json["merchant_details"]["category"]),
                    "zipcode": str(transaction_json["merchant_details"]["zipcode"])
                },
                "payment_type": str(transaction_json["payment_type"])
            }

        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {str(e)}")
            raise
        except json.JSONDecodeError:
            print("API returned invalid JSON or code fences.")
            raise
        except KeyError as e:
            print(f"API response missing expected field: {str(e)}")
            raise
        except ValueError as e:
            print(f"Data validation error: {str(e)}")
            raise

    def generate_transactions(self, output_path: str, target: int = 1000):
        """
        1. Randomly assign each user the subcategories they use (not everyone uses everything).
        2. Decide how many transactions each user gets, to total ~10K across 150 users.
        3. For each transaction, randomly pick one subcategory (based on spending pattern)
           and generate an API call to produce the transaction details.
        4. Save results in CSV.
        """
        self.target_transactions = target
        # Step 1: For each user, pick the subcategories they actually use
        self.customers["user_subcats"] = self.customers.apply(
            lambda _: self._assign_categories_for_user(), axis=1
        )

        # Step 2: Weighted distribution of 10K transactions, based on income
        all_incomes = self.customers["income"].sum()
        self.customers["weight"] = self.customers["income"] / all_incomes
        self.customers["assigned_txn"] = (self.customers["weight"] * self.target_transactions).round().astype(int)

        # Adjust if rounding doesn't sum to 10,000
        total_assigned = self.customers["assigned_txn"].sum()
        diff = self.target_transactions - total_assigned
        if diff > 0:
            indices = self.customers.sample(n=abs(diff), replace=True).index
            self.customers.loc[indices, "assigned_txn"] += 1
        elif diff < 0:
            indices = self.customers.sample(n=abs(diff), replace=True).index
            self.customers.loc[indices, "assigned_txn"] = self.customers["assigned_txn"].clip(lower=0)
            self.customers.loc[indices, "assigned_txn"] -= 1

        transactions = []

        # Step 3: Generate actual transactions
        for _, cust_row in self.customers.iterrows():
            user_dict = cust_row.to_dict()
            n_txn = int(user_dict["assigned_txn"])

            if n_txn <= 0:
                continue

            # Build a spending pattern for the user’s chosen subcategories
            user_subcat_list = user_dict["user_subcats"]
            spending_pattern = self._generate_spending_pattern(user_subcat_list, user_dict)
            total_spend = sum(spending_pattern.values())

            # Convert subcat allocation to probabilities
            subcat_probs = {}
            for subcat, amt in spending_pattern.items():
                if total_spend > 0:
                    subcat_probs[subcat] = amt / total_spend
                else:
                    subcat_probs[subcat] = 0.0

            subcats = list(subcat_probs.keys())
            probs = list(subcat_probs.values())

            for _ in range(n_txn):
                if not subcats:
                    # If user has no subcats, skip
                    break
                chosen_subcat = np.random.choice(subcats, p=probs)
                merchant = self._get_merchant(chosen_subcat, user_dict["zipcode"])
                try:
                    txn = self._generate_transactions_api(user_dict, merchant)
                    transactions.append(txn)
                except Exception as e:
                    print(f"Skipping transaction due to error: {e}")

                # Sleep to avoid rate limiting
                time.sleep(10)

        # Step 4: Save to CSV
        pd.DataFrame(transactions).to_csv(output_path, index=False)
        print(f"Generated {len(transactions)} transactions (Goal: {self.target_transactions})")


if __name__ == "__main__":
    generator = TransactionGenerator(api_key=API_KEY_Groq)
    generator.load_data(
        customers_path="../data/synthetic_customer_gan.csv",
        merchants_path="../data/dc_businesses_cleaned.csv"
    )
    generator.generate_transactions("synthetic_transactions.csv", target=1000)