from src.component.data_part import CSVColumnCleaner

# Define common phrases for replacement
common_phrases = {
    "Estimate!!Number!!HOUSEHOLD INCOME BY AGE OF HOUSEHOLDER!!": "Household Income (",
    "Estimate!!Number!!FAMILIES!!Families!!": "Families ",
    "Estimate!!Number!!FAMILY INCOME BY FAMILY SIZE!!": " ",
    "Estimate!!Number!!FAMILY INCOME BY NUMBER OF EARNERS!!": " ",
    "Estimate!!Number!!NONFAMILY HOUSEHOLDS!!": "",
    "!!": " ",
    "Estimate Median income (dollars) HOUSEHOLD INCOME BY RACE AND HISPANIC OR LATINO ORIGIN OF HOUSEHOLDER Households": "Household Income",
    "Estimate Median income (dollars) HOUSEHOLD INCOME BY AGE OF HOUSEHOLDER": "Household Income (",
    "Estimate Median income (dollars) FAMILIES Families": "Families ",
    "Estimate Median income (dollars) FAMILY INCOME BY FAMILY SIZE": "Income ",
    "Estimate Median income (dollars) FAMILY INCOME BY NUMBER OF EARNERS": "Income ",
    "Estimate Median income (dollars) NONFAMILY HOUSEHOLDS ": "Income ",
}

keywords = {
    "estimate_percent": "Estimate Percent",
    "margin_of_error": "Margin of Error"
}

# Initialize cleaner
cleaner = CSVColumnCleaner(common_phrases, keywords)
# Clean the dataset
input_path = "income_data.csv"
output_path = "cleaned_income_data.csv"

cleaner.clean_csv_columns(input_path, output_path)