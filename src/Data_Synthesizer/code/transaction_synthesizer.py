import pandas as pd
from src.component.transaction import TransactionSimulator
from src.component.transaction import TransactionCTGAN
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
merchants_path = os.path.join(script_dir, 'dc_businesses_cleaned.csv')
customers_path = os.path.join(script_dir, 'synthetic_customers_deepseek.csv')

customers_df = pd.read_csv(customers_path)
merchants_df = pd.read_csv(merchants_path)

# 2) Build a *simulated* transaction dataset for training
sim = TransactionSimulator(customers=customers_df, merchants=merchants_df)

# For demonstration, let's generate e.g. 20 transactions per customer
# Adjust as you like
training_transactions = sim.simulate_transactions(num_per_customer=20)

# 3) Fit CTGAN on the simulated transaction data
model = TransactionCTGAN(epochs=50)
model.fit(training_transactions)

# 4) Generate new synthetic transactions
synthetic_output = model.generate(num_samples=5000)
print(synthetic_output.head(10))

# 5) Save to CSV or do whatever you want
synthetic_output.to_csv("synthetic_transactions_ctgan.csv", index=False)
print(f"Generated {len(synthetic_output)} synthetic transactions.")