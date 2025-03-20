import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import time
import random
from sdv.single_table import CTGANSynthesizer
from sdv.metadata.single_table import SingleTableMetadata
from sdv.errors import SamplingError
import joblib
import torch

class CSVColumnCleaner:
    def __init__(self, common_phrases, keywords):
        self.common_phrases = common_phrases
        self.keywords = keywords

    def clean_column(self, column):
        # Remove unwanted patterns first
        for pattern in self.keywords["remove_patterns"]:
            column = column.replace(pattern, "")

        # Apply phrase replacements
        for phrase, replacement in self.common_phrases.items():
            column = column.replace(phrase, replacement)

        # Final cleanup
        column = column.strip()
        column = column.replace("  ", " ")
        column = column.replace(" )", ")")
        column = column.replace("( ", "(")

        # Standardize numbering formats
        column = column.replace("3 or more", "3+")
        column = column.replace("7-or-more", "7+")

        return column

    def clean_csv_columns(self, input_path, output_path):
        df = pd.read_csv(input_path)

        # Clean columns
        df.columns = [self.clean_column(col) for col in df.columns]

        # Remove empty columns and margin columns
        df = df.loc[:, ~df.columns.str.contains('|'.join(self.keywords["remove_patterns"]))]
        df = df.loc[:, ~df.columns.duplicated()]

        # Group and sum numeric columns with same names
        df = df.groupby(df.columns, axis=1).sum()

        df.to_csv(output_path, index=False)
        return df

class IncomeDataCleaner(BaseEstimator, TransformerMixin):
    """Handles missing values and data formatting for income data, applied to all columns."""

    def __init__(self, critical_columns=['Household Income']):
        """
        Parameters
        ----------
        critical_columns : list
            Columns that are especially important; for these numeric columns,
            we will impute with the median instead of the mean.
            (You can remove or override this if you do not need this distinction.)
        """
        self.critical_columns = critical_columns
        self.imputation_values_ = {}  # will hold imputation values for ALL columns

    def fit(self, X, y=None):
        # Identify columns & store imputation values
        self._identify_columns(X)
        self._calculate_imputation_values(X)
        return self

    def transform(self, X):
        X = X.copy()

        # 1. Convert any currency-like columns to numeric
        X = self._convert_currency_columns(X)

        # 2. Impute missing values in numeric & non-numeric columns
        X = self._impute_missing_values(X)

        # 3. Final validation: ensure no columns have missing values
        self._validate_transformed_data(X)

        return X

    def _identify_columns(self, X):
        """
        Identify numeric and non-numeric columns so we can handle them differently.
        """
        # If you have specific dtypes you consider "numeric,"
        # stick with include=[np.number]
        self.numeric_cols_ = X.select_dtypes(include=[np.number]).columns.tolist()
        self.non_numeric_cols_ = X.select_dtypes(exclude=[np.number]).columns.tolist()

    def _calculate_imputation_values(self, X):
        """
        Calculate the imputation values for every column in the dataset.
        - For numeric columns in `critical_columns`, use median.
        - For numeric columns not in `critical_columns`, use mean.
        - For non-numeric columns, use the mode.
        """
        # Numeric columns
        for col in self.numeric_cols_:
            if col in self.critical_columns:
                # Use median for "critical" numeric columns
                self.imputation_values_[col] = X[col].median()
            else:
                # Use mean for other numeric columns
                self.imputation_values_[col] = X[col].mean()

        # Non-numeric (categorical/string) columns
        for col in self.non_numeric_cols_:
            # Use the most frequent value
            # Note: dropna=False to ensure we count existing NaNs in the frequency
            self.imputation_values_[col] = X[col].mode(dropna=True).iloc[0] \
                if not X[col].mode(dropna=True).empty else ''

    def _convert_currency_columns(self, X):
        """
        Convert currency-formatted columns (e.g. with $ signs, commas) to floats.
        We do this by searching for columns that have 'Income' or 'Dollar' in the name.
        Adjust the detection logic as needed.
        """
        currency_columns = [
            col for col in X.columns
            if any(substr in col for substr in ['Income', 'Dollar'])
        ]

        for col in currency_columns:
            # Only convert if the column is object/string-based
            if X[col].dtype == object:
                # Remove $, commas, etc., then convert to numeric
                X[col] = (X[col]
                          .replace('[\$,]', '', regex=True)
                          .replace(',', '', regex=True))
                X[col] = pd.to_numeric(X[col], errors='coerce')
        return X

    def _impute_missing_values(self, X):
        """
        Fill missing values for all columns using the imputation values
        computed in `fit()`.
        """
        # Impute numeric columns
        for col in self.numeric_cols_:
            if col in X.columns:
                X[col] = X[col].fillna(self.imputation_values_[col])

        # Impute non-numeric columns
        for col in self.non_numeric_cols_:
            if col in X.columns:
                X[col] = X[col].fillna(self.imputation_values_[col])

        return X

    def _validate_transformed_data(self, X):
        """
        Ensure that no columns (especially critical ones) have missing values after transformation.
        """
        # Check for remaining missing values in entire dataset
        if X.isna().any().any():
            missing_cols = X.columns[X.isna().any()].tolist()
            raise ValueError(f"Some columns still contain missing values: {missing_cols}")

        # Ensure that any numeric columns are indeed numeric after transformations
        for col in self.numeric_cols_:
            if col in X.columns and not np.issubdtype(X[col].dtype, np.number):
                raise TypeError(f"Column '{col}' is not numeric after cleaning.")

class IncomeDataProcessor(BaseEstimator, TransformerMixin):
    """Advanced processor for census-style income data,
       building ONE aggregated distribution across all ZIP codes."""

    def __init__(self):
        self.age_brackets = ['15-24', '25-44', '45-64', '65+']

        # Define all required columns for validation
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
            'Number 7-or-more person families', 'Income 7-or-more person families',
            # Target variable
            'Household Income'
        ]
        self.model_ = None  # We'll store the single aggregated distribution here

    def fit(self, X, y=None):
        """Aggregate bracket distributions + average incomes across the entire dataset (all ZIP codes)."""
        self._validate_columns(X)

        # Summation across entire dataset for each bracket => build global distributions
        age_dist = self._calculate_age_distribution(X)
        family_dist = self._calculate_family_distribution(X)
        earner_dist = self._calculate_earner_distribution(X)
        size_dist = self._calculate_household_size(X)

        # Store them as one global model (no per-ZIP logic)
        self.model_ = {
            'age_dist': age_dist,    # { "distribution": {...}, "incomes": {...} }
            'family_dist': family_dist,
            'earner_dist': earner_dist,
            'size_dist': size_dist
        }
        return self

    def transform(self, X):
        """Return the single global model (dict) so we can sample from it downstream."""
        return self.model_

    def _validate_columns(self, X):
        missing = set(self.required_columns) - set(X.columns)
        if missing:
            raise KeyError(f"Missing required columns: {missing}")

    def _calculate_age_distribution(self, df):
        """Aggregate all data to produce a global age distribution + average incomes."""
        age_bracket_map = {
            '15-24': '15 to 24 years',
            '25-44': '25 to 44 years',
            '45-64': '45 to 64 years',
            '65+':   '65 years and over'
        }

        total_count = 0
        dist_counts = {}
        sum_incomes = {}

        for bracket in self.age_brackets:
            num_col = f'Number Household Income ({age_bracket_map[bracket]})'
            inc_col = f'Household Income ({age_bracket_map[bracket]})'

            count_sum = df[num_col].sum()
            income_sum = df[inc_col].sum()
            total_count += count_sum

            dist_counts[bracket] = count_sum
            sum_incomes[bracket] = income_sum

        # Convert raw counts to fractions & compute average incomes
        distribution = {}
        avg_incomes = {}
        for bracket in self.age_brackets:
            # fraction of total
            fraction = dist_counts[bracket]/total_count if total_count>0 else 0
            # average income in bracket
            bracket_avg = 0
            if dist_counts[bracket] > 0:
                bracket_avg = sum_incomes[bracket] / dist_counts[bracket]

            distribution[bracket] = fraction
            avg_incomes[bracket]  = bracket_avg

        return {
            'distribution': distribution,
            'incomes': avg_incomes
        }

    def _calculate_family_distribution(self, df):
        family_types = {
            'Married-couple families': {
                'count_col': 'Number Families Married-couple families',
                'income_col': 'Income Families Married-couple families'
            },
            'Female householder': {
                'count_col': 'Number Families Female householder, no spouse present',
                'income_col': 'Income Families Female householder, no spouse present'
            },
            'Male householder': {
                'count_col': 'Number Families Male householder, no spouse present',
                'income_col': 'Income Families Male householder, no spouse present'
            }
        }
        return self._calc_global_distribution(df, family_types)

    def _calculate_earner_distribution(self, df):
        earner_types = {
            '0':  {'count_col': 'Number No earners',          'income_col': 'Income No earners'},
            '1':  {'count_col': 'Number 1 earner',            'income_col': 'Income 1 earner'},
            '2':  {'count_col': 'Number 2 earners',           'income_col': 'Income 2 earners'},
            '3+': {'count_col': 'Number 3 or more earners',   'income_col': 'Income 3 or more earners'}
        }
        return self._calc_global_distribution(df, earner_types)

    def _calculate_household_size(self, df):
        sizes = {
            '2':  {'count_col': 'Number 2-person families',    'income_col': 'Income 2-person families'},
            '3':  {'count_col': 'Number 3-person families',    'income_col': 'Income 3-person families'},
            '4':  {'count_col': 'Number 4-person families',    'income_col': 'Income 4-person families'},
            '5':  {'count_col': 'Number 5-person families',    'income_col': 'Income 5-person families'},
            '6':  {'count_col': 'Number 6-person families',    'income_col': 'Income 6-person families'},
            '7+': {'count_col': 'Number 7-or-more person families','income_col': 'Income 7-or-more person families'}
        }
        return self._calc_global_distribution(df, sizes)

    def _calc_global_distribution(self, df, bracket_map):
        """
        Summation across the entire DataFrame for each bracket -> fraction + average incomes.
        e.g. bracket_map = {
           'Married-couple families': {'count_col': ..., 'income_col': ...},
           ...
        }
        """
        total = 0
        dist_counts = {}
        sum_incomes = {}

        for bracket, cols in bracket_map.items():
            count_col = cols['count_col']
            inc_col   = cols['income_col']

            c_sum = df[count_col].sum()
            i_sum = df[inc_col].sum()

            total += c_sum

            dist_counts[bracket] = c_sum
            sum_incomes[bracket] = i_sum

        distribution = {}
        bracket_incomes = {}
        for bracket in bracket_map:
            fraction = dist_counts[bracket]/total if total > 0 else 0
            if dist_counts[bracket] > 0:
                bracket_avg = sum_incomes[bracket] / dist_counts[bracket]
            else:
                bracket_avg = 0

            distribution[bracket]   = fraction
            bracket_incomes[bracket] = bracket_avg

        return {
            'distribution': distribution,
            'incomes': bracket_incomes
        }

class ABMGlobalModel:
    """
    A simple agent-based approach that uses a single global model of bracket distributions
    (age, family, earner, size) to generate synthetic customers.

    - Use .set_global_model(...) to supply the bracket distributions from your IncomeDataProcessor.
    - Call .generate_customers(n) to create n synthetic customers with a timing report.
    """

    def __init__(self):
        self.model_ = None  # Will store your bracket distributions { 'age_dist':..., ... }

    def set_global_model(self, global_model):
        """
        global_model: The dictionary from IncomeDataProcessor.model_, e.g.:
          {
            'age_dist':    { 'distribution': {...}, 'incomes': {...} },
            'family_dist': { 'distribution': {...}, 'incomes': {...} },
            'earner_dist': { 'distribution': {...}, 'incomes': {...} },
            'size_dist':   { 'distribution': {...}, 'incomes': {...} },
          }
        """
        self.model_ = global_model

    def generate_customers(self, n=100):
        """
        Generate 'n' synthetic customers. Return a list of dicts.

        We measure the total time it takes to sample all customers.
        """
        if self.model_ is None:
            raise ValueError("No global model set. Call set_global_model(...) first.")

        start_time = time.time()

        results = []
        for _ in range(n):
            cust = self._sample_one_customer()
            results.append(cust)

        end_time = time.time()
        elapsed_sec = end_time - start_time
        print(f"Generated {n} customers in {elapsed_sec:.2f} seconds.")

        return results

    # ----------------------------------------------------------------
    # Internal methods
    # ----------------------------------------------------------------

    def _sample_one_customer(self):
        """
        Sample ONE customer by:
          1) picking bracket from each distribution (age, family, earner, size)
          2) converting bracket to numeric age / earners
          3) combining bracket-level incomes + noise
        """
        # Weighted bracket picks
        age_bracket = self._weighted_choice(self.model_["age_dist"]["distribution"])
        family_bracket = self._weighted_choice(self.model_["family_dist"]["distribution"])
        earner_bracket = self._weighted_choice(self.model_["earner_dist"]["distribution"])
        size_bracket = self._weighted_choice(self.model_["size_dist"]["distribution"])

        # Convert brackets to numeric
        real_age = self._bracket_to_age(age_bracket)
        real_earners = self._parse_earners(earner_bracket)
        real_size = self._parse_household_size(size_bracket)

        # Combine bracket incomes
        age_inc = self.model_["age_dist"]["incomes"][age_bracket]
        fam_inc = self.model_["family_dist"]["incomes"][family_bracket]
        earn_inc = self.model_["earner_dist"]["incomes"][earner_bracket]
        size_inc = self.model_["size_dist"]["incomes"][size_bracket]

        raw_income = (age_inc + fam_inc + earn_inc + size_inc) / 4.0
        stdev = 0.2 * raw_income  # 20% stdev
        final_income = max(5000, np.random.normal(raw_income, stdev))  # clamp min at $5k

        return {
            "age": real_age,
            "family_type": family_bracket,
            "earners": real_earners,
            "household_size": real_size,
            "income": round(final_income, 2)
        }

    def _weighted_choice(self, dist_map):
        """Given a dict e.g. {'15-24': 0.1, '25-44': 0.3, ...} choose a bracket with those probabilities."""
        brackets = list(dist_map.keys())
        weights = np.array(list(dist_map.values()), dtype=float)
        total = weights.sum()
        if total == 0:
            # fallback uniform
            weights = np.ones(len(weights)) / len(weights)
        else:
            weights /= total
        return np.random.choice(brackets, p=weights)

    def _bracket_to_age(self, bracket):
        """Convert bracket like '15-24' => random int in [15..24], '65+' => random in [65..90]."""
        if bracket == '15-24':
            return random.randint(15, 24)
        elif bracket == '25-44':
            return random.randint(25, 44)
        elif bracket == '45-64':
            return random.randint(45, 64)
        elif bracket == '65+':
            return random.randint(65, 90)
        else:
            return random.randint(18, 85)

    def _parse_earners(self, earner_bracket):
        """If bracket is '3+', pick random from [3..5]; else int(...)"""
        if earner_bracket == "3+":
            return random.randint(3, 5)
        else:
            return int(earner_bracket)

    def _parse_household_size(self, size_bracket):
        """If bracket is '7+', pick random from [7..9]; else int(...)"""
        if size_bracket == '7+':
            return random.randint(7, 9)
        else:
            return int(size_bracket)

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


class AdvancedIncomeModel:
    """Enhanced model using SDV 1.19.0 Single-Table CTGAN approach."""

    def __init__(self, epochs=100):
        self.epochs = epochs
        self.preprocessor = DataPreprocessor()
        self.metadata = None
        self.synthesizer = None

    def fit(self, X):
        """1. Preprocess data, 2. Build Metadata, 3. Train CTGANSynthesizer."""
        # 1. Transform data to household-level format
        household_data = self.preprocessor.transform(X)

        # 2. Create Metadata for single-table modeling
        self.metadata = SingleTableMetadata()
        self.metadata.detect_from_dataframe(household_data)

        # Optionally, override column sdtypes:
        self.metadata.update_column('zipcode', sdtype='categorical')
        self.metadata.update_column('age_bracket', sdtype='categorical')
        self.metadata.update_column('marital_status', sdtype='categorical')
        self.metadata.update_column('gender', sdtype='categorical')
        self.metadata.update_column('earners', sdtype='categorical')
        self.metadata.update_column('income', sdtype='numerical')
        self.metadata.update_column('household_size', sdtype='numerical')

        # 3. Create and train the CTGANSynthesizer
        self.synthesizer = CTGANSynthesizer(
            metadata=self.metadata,
            enforce_rounding=False,
            epochs=self.epochs,
            verbose=True
        )
        self.synthesizer.fit(household_data)
        return self

    def generate(self, num_samples=10):
        """Generate synthetic data from the trained synthesizer."""
        synthetic = self.synthesizer.sample(num_rows=num_samples)


        if 'age_bracket' in synthetic.columns:
            def bracket_to_age(bracket):
                if '-' in bracket:
                    low, high = bracket.split('-')
                    return np.random.randint(int(low), int(high) + 1)
                else:
                    # e.g. '65+' bracket
                    return np.random.randint(65, 85)
            synthetic['age'] = synthetic['age_bracket'].apply(bracket_to_age)

        # Convert '3+' earners to random 3-5
        if 'earners' in synthetic.columns:
            def parse_earners(e):
                if e == '3+':
                    return np.random.randint(3, 6)
                return int(e)
            synthetic['earners'] = synthetic['earners'].apply(parse_earners)

        # Return final columns
        return synthetic[['zipcode', 'age', 'marital_status',
                          'household_size', 'income', 'gender', 'earners']]

    def save(self, path):
        """Save the entire synthesizer object using SDV's save method."""
        # SDV's CTGANSynthesizer has its own save/load methods
        self.synthesizer.save(path)

    @classmethod
    def load(cls, path):
        """Load the synthesizer and metadata."""
        # Initialize a new model instance
        model = cls()

        # Load the synthesizer using SDV's method
        model.synthesizer = CTGANSynthesizer.load(path)

        # Extract metadata from the synthesizer
        model.metadata = model.synthesizer.metadata

        return model

    @classmethod
    def _force_cpu_loading(cls, path):
        """Handle GPU-trained model loading on CPU."""
        # Load the synthesizer state manually
        device = torch.device('cpu')
        synthesizer = CTGANSynthesizer(metadata=None)  # Temporary empty initializer
        synthesizer.__dict__.update(torch.load(path, map_location=device))
        synthesizer._model.to(device)
        synthesizer._device = 'cpu'
        return synthesizer

    def _move_to_cpu(self):
        """Move synthesizer components to CPU."""
        self.synthesizer._model.to('cpu')
        self.synthesizer._device = 'cpu'
        # Update other CUDA-dependent attributes if they exist
        if hasattr(self.synthesizer._model, 'optimizer'):
            for state in self.synthesizer._model.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cpu()


def clean_currency_column(df, column_name):
    df[column_name] = df[column_name].replace(r'[\$,]', '', regex=True).astype(float)
    return df
