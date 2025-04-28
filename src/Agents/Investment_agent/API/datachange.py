import pandas as pd

# Load the uploaded CSV file into a DataFrame
file_path = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/final_combined_dataset.csv'
df = pd.read_csv(file_path, low_memory=False)  # Load the file without dtype specifier first

# Specify the dtype for column 16 (assuming it is causing the issue, change 'str' if needed)
df = pd.read_csv(file_path, low_memory=False, dtype={df.columns[16]: str})  # Apply dtype after the file is loaded

# Remove rows where ticker is 'combined_data_processed'
df_cleaned = df[df['ticker'] != 'combined_processed_data']

# Remove the last 6 columns from the DataFrame
df_cleaned = df_cleaned.iloc[:, :-6]

# Save the modified DataFrame to a new CSV file
output_path = '/Users/yashdoshi/capstone5/Capstone_Project/src/app/src/API/modified_data.csv'
df_cleaned.to_csv(output_path, index=False)
