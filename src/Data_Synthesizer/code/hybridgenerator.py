import pandas as pd
import numpy as np
import time
from config import API_KEY_Groq
import os
import sys
# Add the project root directory to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(ROOT_DIR)
print(ROOT_DIR)
from src.component.transaction import TransactionSimulator
from src.component.transaction import TransactionCTGAN
from src.Data_Synthesizer.code.transaction_deepseek_synthesizer import TransactionGenerator
import random


class HybridTransactionGenerator:
    def __init__(self, groq_api_key: str, ctgan_epochs=100):
        self.groq_gen = TransactionGenerator(api_key=groq_api_key)
        self.ctgan = TransactionCTGAN(epochs=ctgan_epochs)
        self.feedback_data = pd.DataFrame()
        self.validation_threshold = 0.7  # Fraud score threshold

    def _combine_data_sources(self, simulated_df, groq_df):
        """Merge and preprocess data from both sources"""
        combined = pd.concat([simulated_df, groq_df], ignore_index=True)

        # Add source marker
        combined['data_source'] = np.where(combined.index < len(simulated_df),
                                           'simulated', 'groq')

        # Common format conversion
        combined['timestamp'] = pd.to_datetime(combined['timestamp'])
        return combined

    def _enrich_with_groq(self, synthetic_df):
        """Add Groq API validation to CTGAN outputs"""
        enriched_data = []
        for _, row in synthetic_df.iterrows():
            try:
                # Generate validation data through Groq API
                merchant = {
                    "Name": row['merchant_name'],
                    "Category": row['mapped_category'],
                    "Zipcode": row['zipcode']
                }
                customer = {
                    "customer_id": row['customer_id'],
                    "income": 75000,  # Default value, can be enhanced
                    "zipcode": row['zipcode']
                }

                txn = self.groq_gen._generate_transactions_api(customer, merchant)
                txn['ctgan_amount'] = row['transaction_amount']
                txn['fraud_score'] = random.random()  # Replace with actual API validation
                enriched_data.append(txn)
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Enrichment failed: {str(e)}")
        return pd.DataFrame(enriched_data)

    def train_hybrid_model(self, customers_path, merchants_path, cycles=3):
        """Main training loop with feedback integration"""
        # Initial Groq data generation
        self.groq_gen.load_data(customers_path, merchants_path)
        self.groq_gen.generate_transactions("groq_transactions.csv", target=1000)
        groq_data = pd.read_csv("groq_transactions.csv")

        # Initial CTGAN training
        sim = TransactionSimulator(customers=pd.read_csv(customers_path),
                                   merchants=pd.read_csv(merchants_path))
        simulated_data = sim.simulate_transactions(num_per_customer=30)

        # Combine datasets
        combined_data = self._combine_data_sources(simulated_data, groq_data)
        self.ctgan.fit(combined_data)

        # Feedback loop training
        for cycle in range(cycles):
            print(f"Training cycle {cycle + 1}/{cycles}")

            # Generate new synthetic data
            synthetic = self.ctgan.generate(num_samples=5000)

            # Validate and enrich with Groq
            validated = self._enrich_with_groq(synthetic)
            valid_data = validated[validated['fraud_score'] < self.validation_threshold]

            # Augment training data
            self.feedback_data = pd.concat([self.feedback_data, valid_data], ignore_index=True)

            # Retrain with augmented dataset
            updated_data = pd.concat([combined_data, self.feedback_data], ignore_index=True)
            self.ctgan.fit(updated_data)

        return self.ctgan

    def generate_enhanced_transactions(self, num_samples=1000):
        """Generate final enhanced transactions"""
        synthetic = self.ctgan.generate(num_samples)
        return self._enrich_with_groq(synthetic.head(num_samples))

    def save_model(self, path):
        """Save trained hybrid model"""
        self.ctgan.save(path)

    @classmethod
    def load_hybrid_model(cls, path, groq_api_key):
        """Load trained model with Groq integration"""
        instance = cls(groq_api_key)
        instance.ctgan = TransactionCTGAN.load(path)
        return instance


# Updated Main Execution
if __name__ == "__main__":
    # Initialize hybrid generator
    hybrid_gen = HybridTransactionGenerator(
        groq_api_key=API_KEY_Groq,
        ctgan_epochs=100
    )

    # Train with feedback loops
    trained_model = hybrid_gen.train_hybrid_model(
        customers_path="../data/synthetic_customer_gan.csv",
        merchants_path="../data/dc_businesses_cleaned.csv",
        cycles=3
    )

    # Generate enhanced transactions
    final_transactions = hybrid_gen.generate_enhanced_transactions(5000)
    final_transactions.to_csv("enhanced_hybrid_transactions.csv", index=False)

    # Save model for API conversion
    hybrid_gen.save_model("hybrid_ctgan_model.pkl")
    print("Model saved and ready for API deployment")