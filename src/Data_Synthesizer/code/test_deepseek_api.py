import pandas as pd

# Corrected path definition (no trailing comma)
CSV_FILE_PATH = "../data/dc_businesses_cleaned.csv"
CATEGORY_TO_REMOVE = "General Business Licenses"


def remove_category_from_csv(file_path, category_to_remove):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Filter out the unwanted category
        original_count = len(df)
        filtered_df = df[df['Category'] != category_to_remove]
        removed_count = original_count - len(filtered_df)

        # Overwrite the original file
        filtered_df.to_csv(file_path, index=False)

        print(f"Removed {removed_count} rows with category '{category_to_remove}'")
        print(f"Updated file saved to '{file_path}'")

    except Exception as e:
        print(f"Error processing file: {e}")
        print("Please verify:")
        print(f"- File exists at: {file_path}")
        print("- No trailing comma in path variable")
        print("- Correct column name 'Category' exists")


# Execute the removal
remove_category_from_csv(CSV_FILE_PATH, CATEGORY_TO_REMOVE)