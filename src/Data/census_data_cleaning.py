from src.component.customer import CSVColumnCleaner

common_phrases = {
    # Age-related columns
    "Estimate!!Number!!HOUSEHOLD INCOME BY AGE OF HOUSEHOLDER!!": "Number Household Income (",
    "Estimate!!Median income (dollars)!!HOUSEHOLD INCOME BY AGE OF HOUSEHOLDER!!": "Household Income (",

    # Family structure columns
    "Estimate!!Number!!FAMILIES!!Families!!": "Number Families ",
    "Estimate!!Median income (dollars)!!FAMILIES!!Families!!": "Income Families ",

    # Earner columns
    "Estimate!!Number!!FAMILY INCOME BY NUMBER OF EARNERS!!": "Number ",
    "Estimate!!Median income (dollars)!!FAMILY INCOME BY NUMBER OF EARNERS!!": "Income ",

    # Household size columns
    "Estimate!!Number!!FAMILY INCOME BY FAMILY SIZE!!": "Number ",
    "Estimate!!Median income (dollars)!!FAMILY INCOME BY FAMILY SIZE!!": "Income ",

    # General cleanup
    "Estimate!!Number!!": "Number ",
    "Estimate!!Median income (dollars)!!": "Income ",
    "Households!!": "",
    "!!": " ",
    "  ": " ",
    "Families ": "",  # Remove redundant "Families"
    "Families": "",  # In some contexts
    "--": " ",
    "One race ": "",
    "Householder": "",
    "origin (of any race)": "",
    "White alone, not Hispanic or Latino": "White non-Hispanic",
    "dollars": ""
}

# Update keywords to remove margin of error columns
keywords = {
    "remove_patterns": [
        "Margin of Error",
        "Percent Distribution",
        "Unnamed",
        "Nonfamily households"
    ]
}

cleaner = CSVColumnCleaner(common_phrases, keywords)
cleaned_df = cleaner.clean_csv_columns("income_data.csv", "cleaned_income_data1.csv")