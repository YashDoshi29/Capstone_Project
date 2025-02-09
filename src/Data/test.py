import numpy as np
import pandas as pd

num_customers = 10

acs_df = pd.read_csv('cache/acs_data_DC.csv')
acs_df['Median_Household_Income'] = pd.to_numeric(acs_df['Median_Household_Income'], errors='coerce')
avg_income = acs_df['Median_Household_Income'].mean()

    # DC-specific demographic adjustments
data = {
    "Customer_ID": [f"DC_CUST{i:06}" for i in range(1, num_customers + 1)],
    "Age": np.random.randint(18, 81, num_customers),
    "Income": np.maximum(
        np.random.lognormal(mean=np.log(avg_income), sigma=0.3, size=num_customers),
        10000
    ).round(2),
    "Gender": np.random.choice(["Male", "Female", "Other"], size=num_customers, p=[0.48, 0.48, 0.04]),
    "Location": np.random.choice(acs_df['Location'], size=num_customers),
    "Marital_Status": np.random.choice(["Married", "Never Married", "Separated", "Divorced", "Widowed"],
                                           size=num_customers, p=[0.5, 0.3, 0.05, 0.1, 0.05]),
    "Has_Children": np.random.choice([True, False], size=num_customers, p=[0.4, 0.6]),
    "Employment_Zone": np.random.choice(["Downtown", "Suburban", "Federal", "Tourist"],  # DC-specific zones
                                            size=num_customers, p=[0.4, 0.3, 0.2, 0.1]),
}

# Add DC-specific housing costs (based on Ward data)
df = pd.DataFrame(data)
df["Monthly_Housing_Cost"] = (df["Income"] * np.random.normal(0.35, 0.07, num_customers) / 12).round(2)
