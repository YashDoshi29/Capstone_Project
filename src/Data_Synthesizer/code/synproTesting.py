import numpy as np
import pandas as pd
import torch
from sklearn.base import BaseEstimator, TransformerMixin

from synpro.model import SynPro

class DataPreprocessor(BaseEstimator, TransformerMixin):
    """Enhanced data processor with full demographic expansion"""

    def __init__(self):
        self.required_columns = [
            'Zipcode',
            # Age distribution columns
            'Number Household Income (15 to 24 years)',
            'Household Income (15 to 24 years)',
            'Number Household Income (25 to 44 years)',
            'Household Income (25 to 44 years)',
            'Number Household Income (45 to 64 years)',
            'Household Income (45 to 64 years)',
            'Number Household Income (65 years and over)',
            'Household Income (65 years and over)',
            # Family structure columns
            'Number Families Married-couple families',
            'Income Families Married-couple families',
            'Number Families Female householder, no spouse present',
            'Income Families Female householder, no spouse present',
            'Number Families Male householder, no spouse present',
            'Income Families Male householder, no spouse present',
            # Earner columns
            'Number No earners', 'Income No earners',
            'Number 1 earner', 'Income 1 earner',
            'Number 2 earners', 'Income 2 earners',
            'Number 3 or more earners', 'Income 3 or more earners',
            # Household size columns
            'Number 2-person families', 'Income 2-person families',
            'Number 3-person families', 'Income 3-person families',
            'Number 4-person families', 'Income 4-person families',
            'Number 5-person families', 'Income 5-person families',
            'Number 6-person families', 'Income 6-person families',
            'Number 7-or-more person families', 'Income 7-or-more person families'
        ]

    def fit(self, X, y=None):
        self._validate_columns(X)
        return self

    def transform(self, X):
        """Convert aggregated data to household-level format with full demographics"""
        households = []

        for _, row in X.iterrows():
            households += self._process_zipcode(row)

        return pd.DataFrame(households)

    def _process_zipcode(self, row):
        zip_households = []
        zipcode = row['Zipcode']

        # Age distribution
        for age_bracket in ['15-24', '25-44', '45-64', '65+']:
            count = row[f'Number Household Income ({self._age_suffix(age_bracket)})']
            income = row[f'Household Income ({self._age_suffix(age_bracket)})']

            for _ in range(int(count)):
                zip_households.append({
                    'zipcode': zipcode,
                    'age_bracket': age_bracket,
                    **self._sample_demographics(row),
                    'income': self._calculate_income(income)
                })

        return zip_households

    def _age_suffix(self, bracket):
        # Convert "15-24" to "15 to 24 years", "65+" to "65 years and over"
        if '-' in bracket:
            return bracket.replace('-', ' to ') + ' years'
        elif '+' in bracket:
            return bracket.replace('+', ' years and over')
        else:
            raise ValueError(f"Unexpected age bracket format: {bracket}")

    def _sample_demographics(self, row):
        """Sample family structure, household size, and earners"""
        return {
            'marital_status': self._sample_marital_status(row),
            'household_size': self._sample_household_size(row),
            'gender': self._sample_gender(row),
            'earners': self._sample_earners(row)
        }

    def _sample_marital_status(self, row):
        family_counts = {
            'married': row['Number Families Married-couple families'],
            'single': (row['Number Families Female householder, no spouse present']
                       + row['Number Families Male householder, no spouse present'])
        }
        total = sum(family_counts.values())
        if total == 0:
            return np.random.choice(['married', 'single'])  # fallback
        return np.random.choice(
            list(family_counts.keys()),
            p=np.array(list(family_counts.values())) / total
        )

    def _sample_household_size(self, row):
        # Map size codes to actual column suffixes
        size_map = {
            '2': '2-person',
            '3': '3-person',
            '4': '4-person',
            '5': '5-person',
            '6': '6-person',
            '7+': '7-or-more person'
        }

        sizes = ['2', '3', '4', '5', '6', '7+']

        # Use the map to construct correct column names
        counts = [row[f'Number {size_map[size]} families'] for size in sizes]

        total = sum(counts)
        if total == 0:
            return 2  # fallback

        chosen = np.random.choice(sizes, p=np.array(counts) / total)
        return int(chosen) if chosen != '7+' else np.random.randint(7, 10)

    def _sample_gender(self, row):
        female = row['Number Families Female householder, no spouse present']
        male = row['Number Families Male householder, no spouse present']
        total = female + male
        if total == 0:
            return np.random.choice(['female', 'male'])  # fallback
        return np.random.choice(
            ['female', 'male'],
            p=[female / total, male / total]
        )

    def _sample_earners(self, row):
        earners = {
            '0': row['Number No earners'],
            '1': row['Number 1 earner'],
            '2': row['Number 2 earners'],
            '3+': row['Number 3 or more earners']
        }
        total = sum(earners.values())
        if total == 0:
            return '0'  # fallback
        return np.random.choice(
            list(earners.keys()),
            p=np.array(list(earners.values())) / total
        )

    def _calculate_income(self, base_income):
        return max(5000, base_income * np.random.normal(1, 0.2))

    def _validate_columns(self, X):
        missing_cols = set(self.required_columns) - set(X.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")


class AdvancedIncomeModelSynPro:
    """Enhanced model using the SynPro synthesizer for single-table data."""

    def __init__(self, epochs=100):
        self.epochs = epochs
        self.preprocessor = DataPreprocessor()  # <== your custom preprocessor, as in your code
        self.synthesizer = None
        self.discrete_columns = [
            'zipcode',
            'age_bracket',
            'marital_status',
            'gender',
            'earners'
            # etc., list all columns you consider categorical
        ]

    def fit(self, X):
        """
        1. Preprocess data
        2. Train SynPro
        """
        # 1. Transform data to your desired "household-level" format
        household_data = self.preprocessor.transform(X)

        # 2. Create and train the SynPro synthesizer
        #    (You can tweak advanced parameters like adv_loss='r1',
        #     enable_spectral_norm=True, mixed_precision=True, etc.)
        self.synthesizer = SynPro(
            epochs=self.epochs,
            verbose=True,
            batch_size=500,  # or any batch size you want
            embedding_dim=128,
            generator_dim=(256, 256),
            discriminator_dim=(256, 256)
        )
        self.synthesizer.fit(household_data, discrete_columns=self.discrete_columns)
        return self

    def generate(self, num_samples=10):
        """
        Generate synthetic data from the trained SynPro model.
        Apply your custom logic for 'age_bracket', 'earners', etc.
        """
        # 1. Generate synthetic data
        synthetic = self.synthesizer.sample(n=num_samples)

        # 2. Convert 'age_bracket' to numeric 'age'
        if 'age_bracket' in synthetic.columns:
            def bracket_to_age(bracket):
                if '-' in str(bracket):
                    low, high = bracket.split('-')
                    return np.random.randint(int(low), int(high) + 1)
                elif str(bracket).endswith('+'):
                    # e.g. '65+' bracket
                    return np.random.randint(65, 85)
                else:
                    # fallback
                    return 30  # or anything default
            synthetic['age'] = synthetic['age_bracket'].apply(bracket_to_age)

        # 3. Convert '3+' earners to random range
        if 'earners' in synthetic.columns:
            def parse_earners(e):
                if e == '3+':
                    return np.random.randint(3, 6)
                try:
                    return int(e)
                except ValueError:
                    return 2  # fallback
            synthetic['earners'] = synthetic['earners'].apply(parse_earners)

        # 4. Return final columns
        return synthetic[['zipcode', 'age', 'marital_status',
                          'household_size', 'income', 'gender', 'earners']]

    def save(self, path):
        """
        Save the entire SynPro synthesizer object to disk.
        """
        # SynPro natively supports .save(path)
        self.synthesizer.save(path)

    @classmethod
    def load(cls, path):
        """
        Load the synthesizer from disk. Return a new model instance.
        """
        model = cls()
        # Using SynPro's native .load() to reconstruct the synthesizer
        loaded_synth = SynPro.load(path)
        model.synthesizer = loaded_synth
        return model

    @classmethod
    def _force_cpu_loading(cls, path):
        """
        Force load a GPU-trained model onto CPU.
        """
        # Because SynPro loads with .load(), we can override device:
        model = cls()
        loaded_synth = SynPro.load(path)
        loaded_synth.set_device('cpu')
        model.synthesizer = loaded_synth
        return model

    def _move_to_cpu(self):
        """
        Manually move the synthesizer from GPU to CPU if already loaded in memory.
        """
        if self.synthesizer is not None:
            self.synthesizer.set_device('cpu')



if __name__ == "__main__":
    # Suppose you have a DataFrame `df` with your raw data
    df = pd.read_csv("../data/cleaned_income_data.csv")

    # Initialize
    advanced_model = AdvancedIncomeModelSynPro(epochs=50)

    # Train
    advanced_model.fit(df)

    # Generate
    synthetic_samples = advanced_model.generate(num_samples=100)
    print(synthetic_samples.head())

    # Save
    advanced_model.save("synpro_income_model.pt")

    # Later or in another script
    loaded_model = AdvancedIncomeModelSynPro.load("synpro_income_model.pt")
    new_synthetic = loaded_model.generate(num_samples=10)
    print(new_synthetic.head())
