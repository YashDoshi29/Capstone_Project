import requests
import pandas as pd
import time

# Census API Configuration
CENSUS_API_KEY = "your_api_key_here"
CENSUS_API_ENDPOINT = "https://api.census.gov/data/2023/acs/acs5"
STATE_FIPS = "11"  # Washington, DC

# **Final Required Variables**
acs_variables = {
    "NAME": "Location",
    "B01001_001E": "Total_Population",
    "B19013_001E": "Median_Household_Income",
    "B12001_001E": "Total_Population_Marital",
    "B12001_002E": "Married",
    "B12001_009E": "Never_Married",
    "B12001_010E": "Separated",
    "B12001_011E": "Divorced",
    "B12001_012E": "Widowed",
    "B09010_001E": "Total_Households",
    "B09010_002E": "Households_With_Children"
}

# Function to fetch ACS data
def fetch_acs_data(state_fips: str, variable_list: list):
    """Fetch ACS data in a single request."""
    get_vars = ",".join(variable_list)
    params = {
        "get": get_vars,
        "for": f"state:{state_fips}",
        "key": CENSUS_API_KEY
    }

    print(f"Fetching ACS data for state: {state_fips}...")
    response = requests.get(CENSUS_API_ENDPOINT, params=params)

    # Error Handling
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return None

    # Convert JSON response to DataFrame
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    return df

# Fetch and clean data
acs_df = fetch_acs_data(STATE_FIPS, list(acs_variables.keys()))

# Rename columns based on the dictionary
acs_df = acs_df.rename(columns=acs_variables)

# Save results
acs_df.to_csv("acs_data_DC.csv", index=False)

# Display sample
print("\nFinal ACS Data Sample:")
print(acs_df.head())

