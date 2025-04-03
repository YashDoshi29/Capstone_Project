import pandas as pd
import uuid
import os


def add_customer_ids(input_csv_path, output_csv_path=None):
    """
    Adds unique customer IDs to a customer data CSV file

    Args:
        input_csv_path: Path to the input CSV file
        output_csv_path: Path to save the output (defaults to input path)
    """
    # Read the customer data
    customers_df = pd.read_csv(input_csv_path)

    # Check if customer_id column already exists
    if 'customer_id' in customers_df.columns:
        print("Warning: customer_id column already exists. No changes made.")
        return customers_df

    # Generate UUID-based customer IDs
    customers_df['customer_id'] = [str(uuid.uuid4()) for _ in range(len(customers_df))]

    # Reorder columns to put customer_id first
    cols = ['customer_id'] + [col for col in customers_df.columns if col != 'customer_id']
    customers_df = customers_df[cols]

    # Save to output path or overwrite input
    save_path = output_csv_path if output_csv_path else input_csv_path
    customers_df.to_csv(save_path, index=False)
    print(f"Successfully added customer IDs to {save_path}")

    return customers_df


# Example usage
if __name__ == "__main__":
    # Path to your customer data CSV
    input_file = "../data/synthetic_customer_gan.csv"
    add_customer_ids(input_file)