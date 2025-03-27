import pandas as pd
import numpy as np
import random
import datetime
import torch

# SDV imports
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer

# ----------------------------------
# 1) HELPER CONSTANTS & FUNCTIONS
# ----------------------------------

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

def random_timestamp_within_30_days() -> str:
    """
    Return a random ISO 8601 timestamp (YYYY-MM-DD HH:MM:SS) within the last 30 days.
    """
    now = datetime.datetime.now()
    # Pick a random number of hours back up to 30 days (~720 hours)
    random_hours = random.randint(0, 30 * 24)
    random_delta = datetime.timedelta(hours=random_hours)
    ts = now - random_delta
    # Add a random minute and second offset
    ts -= datetime.timedelta(
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def generate_spending_pattern(customer: dict) -> dict:
    """
    Generate a spending pattern for the customer based on their income and household size.
    Returns a dictionary of spending fractions per category.
    """
    base_allocation = {
        'groceries': 0.18 + (0.02 if customer.get('household_size', 1) > 2 else 0),
        'dining': 0.12 + (0.03 if customer.get('income', 0) > 75000 else 0),
        'transportation': 0.15,
        'housing': 0.25,
        'entertainment': 0.10,
        'personal_care': 0.08,
        'other': 0.12
    }
    monthly_income = float(customer.get('income', 0)) / 12.0
    return {k: v * monthly_income for k, v in base_allocation.items()}

# ----------------------------------
# 2) TRANSACTION SIMULATOR
# ----------------------------------

class TransactionSimulator:
    """
    Simulate a training dataset of transactions based on customer profiles and merchant data.
    """

    def __init__(self, customers: pd.DataFrame, merchants: pd.DataFrame):
        self.customers = customers.copy()
        self.merchants = merchants.copy()

        # Map merchant categories
        if 'Category' in self.merchants.columns:
            self.merchants['mapped_category'] = self.merchants['Category'].map(CATEGORY_MAPPING)
        else:
            self.merchants['mapped_category'] = None

        self.merchants.dropna(subset=['mapped_category'], inplace=True)

        # Ensure Zipcode is a string
        self.merchants['Zipcode'] = self.merchants['Zipcode'].astype(str)

        # Group merchants by (Zipcode, mapped_category) for fast lookup
        grouped = self.merchants.groupby(['Zipcode', 'mapped_category'])
        self.merchant_dict = {(zipc, cat): group for (zipc, cat), group in grouped}

    def get_merchant(self, category: str, zipcode: str) -> dict:
        """
        Emulate merchant selection:
         - First try to match by (zipcode, category).
         - Fall back to a random merchant of that category.
         - If none exist, return a generic fallback.
        """
        zipcode_str = str(zipcode)
        group = self.merchant_dict.get((zipcode_str, category), None)
        if group is None or len(group) == 0:
            fallback = self.merchants[self.merchants['mapped_category'] == category]
            if len(fallback) == 0:
                return {
                    'merchant_name': f"DC {category.capitalize()} Service",
                    'merchant_category': category
                }
            return fallback.sample(1).iloc[0].to_dict()
        return group.sample(1).iloc[0].to_dict()

    def simulate_transactions(self, num_per_customer=5) -> pd.DataFrame:
        """
        Generate simulated transactions for each customer.
        """
        output_rows = []
        for _, cust in self.customers.iterrows():
            cust_dict = cust.to_dict()
            pattern = generate_spending_pattern(cust_dict)
            for _ in range(num_per_customer):
                category = random.choice(list(pattern.keys()))
                monthly_amount = pattern[category]
                fraction = random.uniform(0.05, 0.30)
                amount = monthly_amount * fraction
                zipcode = cust_dict.get('zipcode', '20001')
                merch = self.get_merchant(category, zipcode)
                row = {
                    'customer_id': cust_dict.get('customer_id', None),
                    'zipcode': zipcode,
                    'category': category,
                    'merchant_name': merch.get('Name', merch.get('merchant_name', "Unknown Merchant")),
                    'mapped_category': merch.get('mapped_category', category),
                    'transaction_amount': round(amount, 2),
                    'timestamp': random_timestamp_within_30_days()
                }
                output_rows.append(row)
        return pd.DataFrame(output_rows)

# ----------------------------------
# 3) CTGAN MODEL FOR TRANSACTIONS
# ----------------------------------

class TransactionCTGAN:
    """
    CTGAN-based synthesizer for generating transaction-level data.
    """

    def __init__(self, epochs=50):
        self.epochs = epochs
        self.metadata = None
        self.synthesizer = None

    def fit(self, transactions_df: pd.DataFrame):
        """
        Build metadata and train CTGAN on transaction data.
        The 'timestamp' column is dropped from the training data.
        """
        # Drop 'timestamp' from training data
        modeling_df = transactions_df.drop(columns=['timestamp'], errors='ignore')

        # Create metadata from the modeling dataframe (without timestamp)
        self.metadata = SingleTableMetadata()
        self.metadata.detect_from_dataframe(data=modeling_df)

        # Update metadata for known column types
        if 'customer_id' in modeling_df.columns:
            self.metadata.update_column('customer_id', sdtype='categorical')
        if 'merchant_name' in modeling_df.columns:
            self.metadata.update_column('merchant_name', sdtype='categorical')
        if 'category' in modeling_df.columns:
            self.metadata.update_column('category', sdtype='categorical')
        if 'mapped_category' in modeling_df.columns:
            self.metadata.update_column('mapped_category', sdtype='categorical')
        if 'zipcode' in modeling_df.columns:
            self.metadata.update_column('zipcode', sdtype='categorical')
        if 'transaction_amount' in modeling_df.columns:
            self.metadata.update_column('transaction_amount', sdtype='numerical')

        self.synthesizer = CTGANSynthesizer(
            metadata=self.metadata,
            enforce_rounding=False,
            epochs=self.epochs,
            verbose=True
        )
        self.synthesizer.fit(modeling_df)

    def generate(self, num_samples=1000) -> pd.DataFrame:
        """
        Generate synthetic transactions and re-add a random timestamp to each row.
        """
        if not self.synthesizer:
            raise RuntimeError("You must fit the model before generating samples.")
        synthetic_df = self.synthesizer.sample(num_rows=num_samples)
        synthetic_df['timestamp'] = [random_timestamp_within_30_days() for _ in range(len(synthetic_df))]
        return synthetic_df

    def save(self, path: str):
        """Save the CTGAN synthesizer."""
        if not self.synthesizer:
            raise RuntimeError("No trained synthesizer to save.")
        self.synthesizer.save(path)

    @classmethod
    def load(cls, path: str):
        """Load a CTGAN synthesizer from disk."""
        model = cls()
        model.synthesizer = CTGANSynthesizer.load(path)
        model.metadata = model.synthesizer.metadata
        return model

    @classmethod
    def load_on_cpu(cls, path: str):
        """Load a GPU-trained model on CPU."""
        device = torch.device('cpu')
        synthesizer = CTGANSynthesizer(metadata=None)
        synthesizer.__dict__.update(torch.load(path, map_location=device))
        synthesizer._model.to(device)
        synthesizer._device = 'cpu'
        model = cls()
        model.synthesizer = synthesizer
        model.metadata = synthesizer.metadata
        return model
