import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import MinMaxScaler


class RealisticCustomerGenerator:
    def __init__(self, income_demographics_df, employment_sectors_df):
        self.income_data = income_demographics_df
        self.employment_data = employment_sectors_df
        self._preprocess_data()

    def _preprocess_data(self):
        """Clean and preprocess input datasets"""
        # Convert income columns to numeric
        income_cols = ['Median_Household_Income', 'Mean_Income', 'Per_Capita_Income']
        self.income_data[income_cols] = self.income_data[income_cols].replace('[\$,]', '', regex=True).astype(float)

        # Normalize employment sector percentages
        sector_cols = self.employment_data.columns[2:]
        self.employment_data[sector_cols] = self.employment_data[sector_cols].div(
            self.employment_data[sector_cols].sum(axis=1), axis=0)

        # Merge datasets on zipcode
        self.combined_data = pd.merge(
            self.income_data,
            self.employment_data,
            on='Zipcode',
            how='left'
        )

    def _calculate_income(self, row):
        """Calculate individual income based on household parameters"""
        base_income = row['Median_Household_Income']

        # Adjust for household characteristics
        income_factor = 1.0
        if row['Marital_Status'] in ['Married', 'Widowed']:
            income_factor *= 1.3
        if row['Number_of_Earners'] > 1:
            income_factor *= 1.2 ** (row['Number_of_Earners'] - 1)
        if row['Has_Children']:
            income_factor *= 0.95  # Conservative adjustment for child expenses

        # Add random variation with truncated normal distribution
        individual_income = base_income * income_factor * np.random.normal(1, 0.15)
        return max(individual_income, 15000)  # Ensure minimum income

    def _assign_employment_sector(self, zipcode):
        """Assign employment sector based on zipcode distribution"""
        sectors = self.employment_data.columns[2:]
        probabilities = self.employment_data.loc[
            self.employment_data['Zipcode'] == zipcode,
            sectors
        ].values[0]

        return np.random.choice(sectors, p=probabilities)

    def generate_household(self, num_customers):
        """Generate realistic households with zipcode-based demographics"""
        # Weight zipcodes by population
        zipcode_choices = self.combined_data['Zipcode'].values
        population_weights = self.combined_data['Population'].values
        population_weights = MinMaxScaler().fit_transform(population_weights.reshape(-1, 1)).flatten()

        households = []
        for _ in range(num_customers):
            # Select zipcode with probability weighted by population
            zipcode = np.random.choice(zipcode_choices, p=population_weights)
            zip_data = self.combined_data[self.combined_data['Zipcode'] == zipcode].iloc[0]

            # Generate household structure
            family_size = np.random.choice(
                [1, 2, 3, 4, 5],
                p=zip_data[['Single_Member', 'Family_Size_2', 'Family_Size_3', 'Family_Size_4', 'Family_Size_5+']]
            )

            has_children = np.random.rand() < zip_data['Households_with_Children']
            num_earners = min(
                np.random.poisson(zip_data['Average_Earners']),
                family_size
            )

            # Marital status based on zipcode demographics
            marital_status = np.random.choice(
                ['Married', 'Never Married', 'Divorced', 'Widowed'],
                p=[
                    zip_data['Married_Households'],
                    zip_data['Never_Married'],
                    zip_data['Divorced'],
                    zip_data['Widowed']
                ]
            )

            # Age distribution based on zipcode
            age = int(stats.norm.rvs(
                loc=zip_data['Median_Age'],
                scale=10,
                size=1
            ).clip(18, 85))

            # Generate gender with zipcode-specific ratio
            gender = np.random.choice(
                ['Male', 'Female'],
                p=[zip_data['Male_Population'], 1 - zip_data['Male_Population']]
            )

            # Employment sector assignment
            employment_sector = self._assign_employment_sector(zipcode)

            household = {
                'Zipcode': zipcode,
                'Age': age,
                'Gender': gender,
                'Marital_Status': marital_status,
                'Family_Size': family_size,
                'Has_Children': has_children,
                'Number_of_Earners': num_earners,
                'Employment_Sector': employment_sector,
                'Median_Household_Income': zip_data['Median_Household_Income'],
                'Household_Type': 'Family' if family_size > 1 else 'Non-Family'
            }

            # Calculate individual income
            household['Estimated_Income'] = self._calculate_income(household)

            households.append(household)

        return pd.DataFrame(households)


# Example Usage
if __name__ == "__main__":
    # Load datasets
    income_demographics = pd.read_csv("zipcode_income_demographics.csv")
    employment_sectors = pd.read_csv("zipcode_employment_sectors.csv")

    # Initialize generator
    generator = RealisticCustomerGenerator(income_demographics, employment_sectors)

    # Generate 1000 realistic customer profiles
    customers = generator.generate_household(1000)

    # Save results
    customers.to_csv("realistic_customer_profiles.csv", index=False)