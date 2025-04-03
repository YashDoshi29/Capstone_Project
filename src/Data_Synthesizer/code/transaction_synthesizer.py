import pandas as pd
import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(ROOT_DIR)
from src.component.transaction import TransactionSimulator
from src.component.transaction import TransactionCTGAN

script_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up from 'code/' and enter the 'data/' folder
data_dir = os.path.join(script_dir, '..', 'data')
data_dir = os.path.abspath(data_dir)  # Convert to absolute path

# Define filenames
merchants_file = 'dc_businesses_cleaned.csv'
customers_file = 'synthetic_customers_deepseek.csv'

# Build the full paths
merchants_path = os.path.join(data_dir, merchants_file)
customers_path = os.path.join(data_dir, customers_file)

customers_df = pd.read_csv(customers_path)
merchants_df = pd.read_csv(merchants_path)

# 2) Build a *simulated* transaction dataset for training
sim = TransactionSimulator(customers=customers_df, merchants=merchants_df)

training_transactions = sim.simulate_transactions(num_per_customer=30)

# 3) Fit CTGAN on the simulated transaction data
model = TransactionCTGAN(epochs=100)
model.fit(training_transactions)

# 4) Generate new synthetic transactions
synthetic_output = model.generate(num_samples=500000)
print(synthetic_output.head(10))

# 5) Save to CSV or do whatever you want
synthetic_output.to_csv("synthetic_transactions_ctgan.csv", index=False)
print(f"Generated {len(synthetic_output)} synthetic transactions.")