import numpy as np
import pandas as pd
import json
import requests
from datetime import datetime, timedelta

# Configuration
DEEPSEEK_API_KEY = "sk-20f42785068042f1b9d02719d2e22fc6"
API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"


def generate_synthetic_customers(num_customers: int, acs_df: pd.DataFrame) -> pd.DataFrame:
    """Generate detailed customer profiles with DC-specific attributes."""
    acs_df = acs_df.copy()
    acs_df['Median_Household_Income'] = pd.to_numeric(acs_df['Median_Household_Income'], errors='coerce')
    avg_income = acs_df['Median_Household_Income'].mean()

    # DC-specific demographic adjustments
    data = {
        "Customer_ID": [f"DC_CUST{i:06}" for i in range(1, num_customers + 1)],
        "Age": np.random.randint(18, 81, num_customers),
        "Income": np.maximum(
            np.random.lognormal(mean=np.log(avg_income), sigma=0.3, size=num_customers),
            10000
        ).round(2),
        "Gender": np.random.choice(["Male", "Female", "Other"], size=num_customers, p=[0.48, 0.48, 0.04]),
        "Location": np.random.choice(acs_df['Location'], size=num_customers),
        "Marital_Status": np.random.choice(["Married", "Never Married", "Separated", "Divorced", "Widowed"],
                                           size=num_customers, p=[0.5, 0.3, 0.05, 0.1, 0.05]),
        "Has_Children": np.random.choice([True, False], size=num_customers, p=[0.4, 0.6]),
        "Employment_Zone": np.random.choice(["Downtown", "Suburban", "Federal", "Tourist", "Industrial", "University"],  # DC-specific zones
                                            size=num_customers, p=[0.35, 0.25, 0.10, 0.05, 0.15, 0.1]),
    }

    
    # Add DC-specific housing costs (based on Ward data)
    df = pd.DataFrame(data)
    df["Monthly_Housing_Cost"] = (df["Income"] * np.random.normal(0.35, 0.07, num_customers) / 12).round(2)

    return df


class SyntheticDataGenerator:
    def __init__(self, acs_data, merchants_data):
        self.acs_data = acs_data
        self.merchants_data = merchants_data
        self.merchant_cache = {}

    def _deepseek_api_call(self, prompt: str, max_retries: int = 3) -> dict:
        """Generic DeepSeek API caller with error handling"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    API_ENDPOINT,
                    headers=headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 150,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    return json.loads(response.json()["choices"][0]["message"]["content"])

            except Exception as e:
                print(f"API attempt {attempt + 1} failed: {str(e)}")

        return {}  # Return empty dict for fallback

    def generate_customer_profile(self, num_customers: int) -> pd.DataFrame:
        """Generate DC residents with enhanced demographics using DeepSeek"""
        # Base customer generation (from previous code)
        customers = generate_synthetic_customers(num_customers, self.acs_data)

        # Enhance with DeepSeek-generated personas
        enhanced_profiles = []
        for _, customer in customers.iterrows():
            prompt = f"""Generate a detailed consumer persona for a {customer['Age']}-year-old 
            {customer['Gender']} living in {customer['Location']}, DC. Include JSON format with:
            - spending_priorities (array of top 3 priorities)
            - financial_habits (array of 2-3 habits)
            - common_purchases (array of 5 typical items/services)
            - weekend_activities (array of 3 activities)"""

            persona = self._deepseek_api_call(prompt)

            enhanced_profiles.append({
                **customer.to_dict(),
                **persona  # Merge DeepSeek-generated attributes
            })

        return pd.DataFrame(enhanced_profiles)

    def generate_transaction_description(self, customer: dict, merchant: dict) -> str:
        """Generate context-aware transaction descriptions"""
        cache_key = f"{customer['Customer_ID']}-{merchant['Business Name']}"
        if cache_key in self.merchant_cache:
            return self.merchant_cache[cache_key]

        # Use latitude and longitude to provide location context
        lat = merchant.get('Latitude', 'N/A')
        lon = merchant.get('Longitude', 'N/A')
        location_info = f"at coordinates ({lat}, {lon})"

        prompt = f"""Generate a realistic transaction description for a {customer['Age']}-year-old
        {customer['Gender']} {customer['Employment_Zone']} worker at {merchant['Business Name']} 
        ({merchant['Category']}) {location_info}, DC. Consider their likely purpose:
        {customer.get('common_purchases', [])}"""

        result = self._deepseek_api_call(prompt)
        description = result.get("description", f"Purchase at {merchant['Business Name']}")

        self.merchant_cache[cache_key] = description
        return description

    def predict_spending_pattern(self, customer: dict) -> dict:
        """Use DeepSeek to predict category weights based on customer profile"""
        prompt = f"""Predict weekly spending distribution (%) for these DC resident attributes:
        - Age: {customer['Age']}
        - Income: ${customer['Income']:,.2f}
        - Location: {customer['Location']}
        - Employment Zone: {customer['Employment_Zone']}
        - Priorities: {customer.get('spending_priorities', [])}

        Return JSON with category percentages for: Food, Housing, Transportation, Healthcare, 
        Entertainment, Retail, Government, Education, Travel, Miscellaneous"""

        distribution = self._deepseek_api_call(prompt)

        # Fallback to default DC distribution
        default_dist = {
            "Food": 18, "Housing": 25, "Transportation": 12, "Healthcare": 7,
            "Entertainment": 10, "Retail": 12, "Government": 5, "Education": 3,
            "Travel": 5, "Miscellaneous": 3
        }

        return distribution if distribution else default_dist

    def generate_transactions(self, customer_df: pd.DataFrame, num_weeks: int = 4) -> pd.DataFrame:
        """Main transaction generator with DeepSeek integration"""
        customer = customer_df.iloc[0].to_dict()
        transactions = []

        # Get AI-predicted spending pattern
        spending_dist = self.predict_spending_pattern(customer)
        total = sum(spending_dist.values())
        spending_dist = {k: v / total for k, v in spending_dist.items()}

        # Budget calculation (from previous code)
        tax_rate = 0.2 + (customer["Income"] > 100000) * 0.05
        essentials = customer["Monthly_Housing_Cost"] + 200
        discretionary = (customer["Income"] / 12 * (1 - tax_rate)) - essentials
        weekly_budget = max(discretionary / 4.33, 50)

        # Transaction generation loop
        for week in range(num_weeks):
            category_budgets = {k: v * weekly_budget for k, v in spending_dist.items()}

            for category, budget in category_budgets.items():
                # Get DC merchants in category
                merchants = self.merchants_data[
                    self.merchants_data['Category'].str.contains(category, case=False)
                ]

                if not merchants.empty and budget > 5:
                    num_txns = max(1, int(budget // np.random.uniform(20, 50)))
                    amounts = np.random.dirichlet(np.ones(num_txns)) * budget

                    for amount in amounts:
                        merchant = merchants.sample(1).iloc[0]
                        description = self.generate_transaction_description(customer, merchant)

                        # Call _generate_dc_timestamp with all required arguments
                        timestamp = self._generate_dc_timestamp(
                            week_offset=week,
                            base_date=datetime.now(),
                            category=category,
                            employment_zone=customer["Employment_Zone"]
                        )

                        transactions.append({
                            "Customer_ID": customer["Customer_ID"],
                            "Timestamp": timestamp,
                            "Amount": round(amount, 2),
                            "Category": category,
                            "Merchant": merchant["Business Name"],
                            "Description": description,
                            "Payment_Type": np.random.choice(["Credit", "Debit"], p=[0.7, 0.3]),
                            # Call _is_online with both category and merchant parameters
                            "Online": self._is_online(category, merchant)
                        })

        return pd.DataFrame(transactions)

    # Helper methods from previous implementation
    def _generate_dc_timestamp(self, week_offset: int, base_date: datetime, category: str, employment_zone: str) -> str:
        """Generate realistic DC timestamps based on category and employment zone."""
        # day_offset = np.random.randint(0, 7)
        # transaction_date = base_date - timedelta(days=day_offset)
        
        transaction_date = base_date - timedelta(weeks=week_offset)

        employment_zone_hours = {
        "Downtown": [7, 8, 9, 16, 17, 18],  # Federal work hours
        "Suburban": [8, 9, 12, 17, 18, 19],  # Office work hours
        "Industrial": [6, 7, 15, 16, 17, 18],  # Factory shifts
        "University": [10, 12, 14, 18, 20, 21],  # Student hours
        "Federal": [6, 7, 8, 16, 17, 18],  # Federal early morning and evening
        "Tourist": [9, 11, 13, 15, 17, 19]  # Tourist-heavy business hours
    }
        
        category_hours = {
        "Food": [11, 12, 13, 18, 19, 20],  # Meal times
        "Housing": [9, 10, 14, 15],  # Business hours for housing-related transactions
        "Transportation": [7, 8, 17, 18],  # Commute times
        "Healthcare": [9, 10, 14, 15],  # Business hours for healthcare
        "Entertainment": [18, 19, 20, 21, 22],  # Evening entertainment
        "Retail": [10, 11, 12, 17, 18, 19],  # Shopping hours
        "Government": [9, 10, 14, 15],  # Government office hours
        "Education": [10, 11, 12, 14, 15, 16],  # School hours
        "Travel": [9, 10, 14, 15],  # Business hours for travel
        "Miscellaneous": [10, 11, 12, 14, 15, 16]  # General business hours
    }
       
        if employment_zone in employment_zone_hours:
            zone_hours = employment_zone_hours[employment_zone]
        else:
            zone_hours = [9, 10, 11, 12, 14, 15, 16, 17]  # Default business hours
        
        if category in category_hours:
            category_hours_list = category_hours[category]
        else:
            category_hours_list = [10, 11, 12, 14, 15, 16]  # Default business hours
        
        # Intersection of zone and category hours
        possible_hours = list(set(zone_hours).intersection(set(category_hours_list)))
        
        if not possible_hours:
            possible_hours = [10, 11, 12, 14, 15, 16]  # Default to general business hours
        
        # Randomly select an hour from the possible hours
        hour = np.random.choice(possible_hours)
        
        # Randomly select a minute
        minute = np.random.randint(0, 60)
        
        # Generate the timestamp
        timestamp = transaction_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    def _is_online(self, category: str, merchant: dict) -> bool:
        """Determine if transaction is online based on merchant type."""
        if "Online" in merchant.get("Business Type", ""):
            return True
        return np.random.choice([True, False], p=[0.3, 0.7]) if category in ["Retail", "Education"] else False


# Usage Example
if __name__ == "__main__":
    # Initialize generator
    acs_data = pd.read_csv("./acs_data_DC.csv")
    merchants_data = pd.read_csv("cache/dc_businesses_cleaned.csv")
    generator = SyntheticDataGenerator(acs_data, merchants_data)

    # Generate enhanced customer profile
    customer = generator.generate_customer_profile(1)

    # Generate transactions with AI-enhanced features
    transactions = generator.generate_transactions(customer, num_weeks=4)

    # Save results
    customer.to_csv("ai_enhanced_customer.csv", index=False)
    transactions.to_csv("ai_enhanced_transactions.csv", index=False)
