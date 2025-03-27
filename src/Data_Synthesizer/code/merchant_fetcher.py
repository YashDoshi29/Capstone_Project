import os
import requests
import pandas as pd

# API endpoint for DC business licenses
API_URL = "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/DCRA/MapServer/0/query"

# File paths
CACHE_DIR = "cache"
RAW_CSV = os.path.join(CACHE_DIR, "dc_active_businesses_full.csv")
CLEANED_CSV = os.path.join(CACHE_DIR, "dc_businesses_cleaned.csv")

# ✅ Define relevant business categories for consumer transactions
RELEVANT_CATEGORIES = [
    "General Business Licenses", "Grocery Store", "Restaurant", "Caterers", "Delicatessen",
    "Bakery", "Food Products", "Food Vending Machine", "Mobile Delicatessen", "Marine Food Retail",
    "Ice Cream Manufacture", "Gasoline Dealer", "Auto Rental", "Tow Truck", "Tow Truck Business",
    "Tow Truck Storage Lot", "Auto Wash", "Driving School", "Motion Picture Theatre", "Public Hall",
    "Skating Rink", "Special Events", "Theater (Live)", "Billiard Parlor", "Bowling Alley",
    "Athletic Exhibition", "Bed and Breakfast", "Boarding House", "Hotel", "Inn And Motel",
    "Vacation Rental", "Beauty Shop", "Beauty Shop Nails", "Beauty Booth", "Barber Shop",
    "Beauty Shop Esthetics", "Health Spa", "Massage Establishment", "Beauty Shop Braiding",
    "Beauty Shop Electrology"
]

# ✅ Define columns to keep
COLUMNS_TO_KEEP = {
    "ENTITY_NAME": "Name",
    "LICENSECATEGORY": "Category",
    "SITE_ADDRESS": "Address",
    "CITY": "City",
    "STATE": "State",
    "ZIP": "Zipcode",
    "PHONE_NUMBER": "Phone",
    "LATITUDE": "Latitude",
    "LONGITUDE": "Longitude"
}


def fetch_all_active_dc_businesses():
    """Fetch all Active businesses in Washington, DC using pagination."""
    all_records = []
    offset = 0

    params = {
        "where": "LICENSESTATUS='Active' AND STATE='DC'",  # Fetch only active businesses in DC
        "outFields": "*",  # Retrieve all fields
        "outSR": "4326",  # Use latitude/longitude for mapping
        "f": "json",  # Return data in JSON format
        "resultRecordCount": 2000,  # Max records per request
        "resultOffset": offset  # Start from the first record
    }

    while True:
        print(f"🌐 Fetching records with offset: {offset}...")
        params["resultOffset"] = offset  # Update offset for pagination

        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract business records
            businesses = data.get("features", [])
            if not businesses:
                print("✅ No more records to fetch.")
                break  # Stop when no more data is available

            # Convert JSON attributes into a list of dictionaries
            records = [biz["attributes"] for biz in businesses]
            all_records.extend(records)

            # Update offset for the next batch
            offset += len(records)

        except requests.exceptions.RequestException as e:
            print(f"❌ API Request Failed: {e}")
            break

    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    print(f"✅ Successfully retrieved {len(df)} Active business records.")
    return df


def clean_dc_businesses(input_csv, output_csv):
    """Cleans and filters the DC business dataset based on relevant categories."""
    print("📂 Loading dataset for cleaning...")
    df = pd.read_csv(input_csv)

    # ✅ Ensure all businesses are in DC and have active licenses
    df = df[(df["STATE"].str.upper() == "DC") & (df["LICENSESTATUS"].str.lower() == "active")]

    # ✅ Keep only necessary columns and rename them
    df = df[list(COLUMNS_TO_KEEP.keys())].rename(columns=COLUMNS_TO_KEEP)

    # ✅ Filter only businesses in relevant categories
    df = df[df["Category"].isin(RELEVANT_CATEGORIES)]

    # ✅ Handle missing values
    df.fillna({"Business Name": "Unknown", "Category": "Unknown", "Address": "Unknown",
               "Phone": "Not Available", "Latitude": 0.0, "Longitude": 0.0}, inplace=True)

    # ✅ Save cleaned data
    df.to_csv(output_csv, index=False)

    print(f"✅ Cleaned dataset saved to {output_csv} with {len(df)} records.")


def cache_merchant_data():
    """Caches business license data to avoid repeated API calls."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Step 1: Fetch and Cache Raw Data_Synthesizer
    if not os.path.exists(RAW_CSV) or os.path.getsize(RAW_CSV) == 0:
        print("🌐 Fetching fresh merchant data from API...")
        merchants_df = fetch_all_active_dc_businesses()
        if merchants_df.empty:
            print("🚨 No data fetched from API. Check API response.")
            return pd.DataFrame()
        merchants_df.to_csv(RAW_CSV, index=False)
    else:
        print("📂 Loading merchant data from cache...")
        merchants_df = pd.read_csv(RAW_CSV)

    # Step 2: Clean and Cache Processed Data_Synthesizer
    if not os.path.exists(CLEANED_CSV) or os.path.getsize(CLEANED_CSV) == 0:
        clean_dc_businesses(RAW_CSV, CLEANED_CSV)

    return pd.read_csv(CLEANED_CSV)

# Run fetch and clean function if executed directly
if __name__ == "__main__":
    merchants_df = cache_merchant_data()
    print("✅ Merchant Data_Synthesizer Sample:")
    print(merchants_df.head())
