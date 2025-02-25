import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
from sklearn.base import BaseEstimator, TransformerMixin
import pymc as pm
import arviz as az


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



#Customer data synthesizer

class IncomeDataProcessor(BaseEstimator, TransformerMixin):
    """Advanced processor for census-style income data"""

    def __init__(self):
        self.age_brackets = ['15-24', '25-44', '45-64', '65+']
        self.family_columns = ['Married-couple families', 'Female householder', 'Male householder']

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

    def fit(self, X, y=None):
        self._validate_columns(X)
        self.zipcode_stats_ = {}

        for zipcode in X['Zipcode'].unique():
            # Get data for current zipcode
            zip_data = X[X['Zipcode'] == zipcode]

            # Calculate statistics for this zipcode
            stats = {
                'age_dist': self._calculate_age_distribution(zip_data),
                'family_dist': self._calculate_family_distribution(zip_data),
                'earner_dist': self._calculate_earner_distribution(zip_data),
                'household_size_dist': self._calculate_household_size(zip_data),
                'income_model': self._build_bayesian_model(zip_data)
            }
            self.zipcode_stats_[zipcode] = stats
        return self

    def transform(self, X):
        return self.zipcode_stats_

    def _validate_columns(self, X):
        missing = set(self.required_columns) - set(X.columns)
        if missing:
            raise KeyError(f"Missing required columns: {missing}")

    def _calculate_age_distribution(self, zip_data):
        age_bracket_map = {
            '15-24': '15 to 24 years',
            '25-44': '25 to 44 years',
            '45-64': '45 to 64 years',
            '65+': '65 years and over'
        }

        household_counts = {
            bracket: zip_data[f'Number Household Income ({age_bracket_map[bracket]})'].values[0]
            for bracket in self.age_brackets
        }
        total_households = sum(household_counts.values())

        return {
            'distribution': {b: c / total_households for b, c in household_counts.items()},
            'median_incomes': {
                bracket: zip_data[f'Household Income ({age_bracket_map[bracket]})'].values[0]
                for bracket in self.age_brackets
            }
        }

    def _calculate_family_distribution(self, zip_data):
        family_types = {
            'married': {
                'count_col': 'Number Families Married-couple families',
                'income_col': 'Income Families Married-couple families'
            },
            'female_head': {
                'count_col': 'Number Families Female householder, no spouse present',
                'income_col': 'Income Families Female householder, no spouse present'
            },
            'male_head': {
                'count_col': 'Number Families Male householder, no spouse present',
                'income_col': 'Income Families Male householder, no spouse present'
            }
        }

        counts = {k: zip_data[v['count_col']].values[0] for k, v in family_types.items()}
        total = sum(counts.values())

        return {
            'distribution': {k: v / total for k, v in counts.items()},
            'incomes': {k: zip_data[v['income_col']].values[0] for k, v in family_types.items()}
        }

    def _calculate_earner_distribution(self, zip_data):
        earner_types = {
            '0': {'count_col': 'Number No earners', 'income_col': 'Income No earners'},
            '1': {'count_col': 'Number 1 earner', 'income_col': 'Income 1 earner'},
            '2': {'count_col': 'Number 2 earners', 'income_col': 'Income 2 earners'},
            '3+': {'count_col': 'Number 3 or more earners', 'income_col': 'Income 3 or more earners'}
        }

        counts = {k: zip_data[v['count_col']].values[0] for k, v in earner_types.items()}
        total = sum(counts.values())

        return {
            'distribution': {k: v / total for k, v in counts.items()},
            'incomes': {k: zip_data[v['income_col']].values[0] for k, v in earner_types.items()}
        }

    def _calculate_household_size(self, zip_data):
        sizes = {
            '2': {'count_col': 'Number 2-person families', 'income_col': 'Income 2-person families'},
            '3': {'count_col': 'Number 3-person families', 'income_col': 'Income 3-person families'},
            '4': {'count_col': 'Number 4-person families', 'income_col': 'Income 4-person families'},
            '5': {'count_col': 'Number 5-person families', 'income_col': 'Income 5-person families'},
            '6': {'count_col': 'Number 6-person families', 'income_col': 'Income 6-person families'},
            '7+': {'count_col': 'Number 7-or-more person families', 'income_col': 'Income 7-or-more person families'}
        }

        counts = {k: zip_data[v['count_col']].values[0] for k, v in sizes.items()}
        total = sum(counts.values())

        return {
            'distribution': {k: v / total for k, v in counts.items()},
            'incomes': {k: zip_data[v['income_col']].values[0] for k, v in sizes.items()}
        }

    def _build_bayesian_model(self, zip_data):
        # Fetch your calculated distributions
        age_data = self._calculate_age_distribution(zip_data)
        family_data = self._calculate_family_distribution(zip_data)
        earner_data = self._calculate_earner_distribution(zip_data)
        size_data = self._calculate_household_size(zip_data)

        with pm.Model() as income_model:
            # Convert dictionary values to numpy arrays
            # and ensure they are strictly positive for Dirichlet
            tiny = 1e-3  # small constant to avoid zeros in the Dirichlet
            age_probs = np.array(list(age_data['distribution'].values()), dtype=np.float64)
            family_probs = np.array(list(family_data['distribution'].values()), dtype=np.float64)
            earner_probs = np.array(list(earner_data['distribution'].values()), dtype=np.float64)
            size_probs = np.array(list(size_data['distribution'].values()), dtype=np.float64)

            # Add tiny if needed to avoid zeros:
            age_probs = np.clip(age_probs, tiny, None)
            family_probs = np.clip(family_probs, tiny, None)
            earner_probs = np.clip(earner_probs, tiny, None)
            size_probs = np.clip(size_probs, tiny, None)

            # Define Dirichlet priors
            age_weights = pm.Dirichlet('age_weights', a=age_probs)
            family_weights = pm.Dirichlet('family_weights', a=family_probs)
            earner_weights = pm.Dirichlet('earner_weights', a=earner_probs)
            size_weights = pm.Dirichlet('size_weights', a=size_probs)

            # Convert incomes to float arrays
            # Make sure the lengths match the above distributions
            age_mu = np.array(list(age_data['median_incomes'].values()), dtype=np.float64)
            family_mu = np.array(list(family_data['incomes'].values()), dtype=np.float64)
            earner_mu = np.array(list(earner_data['incomes'].values()), dtype=np.float64)
            size_mu = np.array(list(size_data['incomes'].values()), dtype=np.float64)

            # Compute the linear combination of means
            # Each dot(...) yields a scalar if shapes match
            mu_income = (
                    pm.math.dot(age_weights, age_mu)
                    + pm.math.dot(family_weights, family_mu)
                    + pm.math.dot(earner_weights, earner_mu)
                    + pm.math.dot(size_weights, size_mu)
            )

            # Prior for sigma
            sigma = pm.HalfNormal('sigma', sigma=1e5)

            # Observed data
            # If zip_data['Household Income'] is just one row, this might be a single float
            observed_income = zip_data['Household Income'].values[0].astype(np.float64)
            # If you have multiple data points, remove [0] and keep the full array

            # Likelihood
            pm.Normal(
                'income',
                mu=mu_income,
                sigma=sigma,
                observed=observed_income
            )

        return income_model


class IndividualIncomePredictor:
    """Predict individual income using pre-computed zipcode statistics with full demographic integration."""

    def __init__(self, zipcode_stats):
        """
        Parameters
        ----------
        zipcode_stats : dict
            This is the output from IncomeDataProcessor.transform(df).
            For each zipcode, you have a dictionary with:
              {
                'age_dist': {
                  'distribution': {'15-24': p1, '25-44': p2, '45-64': p3, '65+': p4},
                  'median_incomes': {'15-24': inc1, '25-44': inc2, '45-64': inc3, '65+': inc4}
                },
                'family_dist': {
                  'distribution': {'married': pm, 'female_head': pf, 'male_head': ph},
                  'incomes': {'married': im, 'female_head': if_, 'male_head': ih}
                },
                'earner_dist': {
                  'distribution': {'0': p0, '1': p1, '2': p2, '3+': p3plus},
                  'incomes': {'0': i0, '1': i1, '2': i2, '3+': i3plus}
                },
                'household_size_dist': {
                  'distribution': {'2': p2, '3': p3, '4': p4, '5': p5, '6': p6, '7+': p7plus},
                  'incomes': {'2': i2, '3': i3, '4': i4, '5': i5, '6': i6, '7+': i7plus}
                },
                'income_model': <PyMC model object>   # not used directly here, but available if needed
              }
        """
        self.zipcode_stats = zipcode_stats

    def predict_individual(self, num_samples=1):
        """
        Generate synthetic individuals by sampling demographics and applying an income model.
        By default, this returns `num_samples` individuals *per* ZIP code in `self.zipcode_stats`.
        """
        individuals = []

        for zipcode, stats in self.zipcode_stats.items():
            # Each 'stats' has keys: 'age_dist','family_dist','earner_dist','household_size_dist','income_model'
            age_data = stats['age_dist']
            family_data = stats['family_dist']
            earner_data = stats['earner_dist']
            size_data = stats['household_size_dist']

            # Sample `num_samples` individuals for this ZIP
            for _ in range(num_samples):
                # 1) Sample demographics from the distributions
                demographics = self._sample_demographics(
                    zipcode,
                    age_data['distribution'],
                    family_data['distribution'],
                    earner_data['distribution'],
                    size_data['distribution']
                )

                # 2) Calculate a base income from the stored median/family incomes
                base_income = self._calculate_base_income(demographics)

                # 3) Apply additional (realistic) adjustments
                final_income = self._apply_realistic_adjustments(base_income, demographics)

                individuals.append({
                    **demographics,
                    'income': final_income
                })

        return pd.DataFrame(individuals)

    def _sample_demographics(self, zipcode, age_dist, family_dist, earner_dist, size_dist):
        """
        Sample a random individual's demographics from the dictionary-based distributions.
        - For 'age_group', we sample from {'15-24','25-44','45-64','65+'}
        - For 'family_type', we sample from {'married','female_head','male_head'}
        - For 'earners', we sample from {'0','1','2','3+'}
        - For 'household_size', we sample from {'2','3','4','5','6','7+'}
        """
        return {
            'zipcode': zipcode,
            'age_group': np.random.choice(
                list(age_dist.keys()),
                p=list(age_dist.values())
            ),
            'family_type': np.random.choice(
                list(family_dist.keys()),
                p=list(family_dist.values())
            ),
            'earners': self._sample_earners(earner_dist),
            'household_size': self._parse_household_size(
                np.random.choice(list(size_dist.keys()), p=list(size_dist.values()))
            )
        }

    def _calculate_base_income(self, demographics):
        """
        Compute a 'base' income using the demographic-based incomes from self.zipcode_stats.
        We combine them with some weighting (0.4,0.3,0.2,0.1).
        """
        zipcode = demographics['zipcode']
        stats = self.zipcode_stats[zipcode]

        # Grab the correct key for earners
        earner_count = demographics['earners']
        earner_key = '3+' if earner_count >= 3 else str(earner_count)

        # Grab the correct key for household size
        # If it's int >=7, we map it to '7+'
        hsize = demographics['household_size']
        if isinstance(hsize, int) and hsize >= 7:
            size_key = '7+'
        else:
            size_key = str(hsize)

        # Age income
        age_income = stats['age_dist']['median_incomes'][demographics['age_group']]
        # Family income
        family_income = stats['family_dist']['incomes'][demographics['family_type']]
        # Earner income
        earner_income = stats['earner_dist']['incomes'][earner_key]
        # Size income
        size_income = stats['household_size_dist']['incomes'][size_key]

        # Weighted combination (example: 0.4,0.3,0.2,0.1)
        base_inc = (
            0.4 * age_income +
            0.3 * family_income +
            0.2 * earner_income +
            0.1 * size_income
        )
        return base_inc

    def _apply_realistic_adjustments(self, base_income, demographics):
        """
        Adjust income based on household size, number of earners, and family type.
        """
        # Convert household_size to integer if needed
        household_size = demographics['household_size']
        if not isinstance(household_size, int):
            # If we stored '7+' or something, parse it
            try:
                household_size = int(household_size)
            except ValueError:
                # fallback if string like '7+'
                household_size = 7

        # For any size >=7, clamp or keep as is
        if household_size < 1:
            household_size = 1

        # Example size factor: bigger households => smaller per-person factor
        size_factor = 1.0 / (household_size ** 0.15)

        # Adjust for family type
        family_mult = {
            'married': 1.15,
            'female_head': 1.05,
            'male_head': 1.07
        }.get(demographics['family_type'], 1.0)

        # If there are zero earners, set income to 0
        if demographics['earners'] == 0:
            return 0.0

        # earner_factor: each additional earner beyond the first +18%
        earner_factor = 1.0 + 0.18 * (demographics['earners'] - 1)

        # Combine
        varied_income = base_income * size_factor * earner_factor * family_mult
        # Add random lognormal noise
        varied_income *= np.random.lognormal(mean=0, sigma=0.1)

        # Enforce a minimum
        return max(varied_income, 15000)

    def _parse_household_size(self, size_str):
        """
        Convert household size strings to numerical or clamp them to '7+' if needed.
        If you want a distribution for '7+', you can do so here.
        """
        if size_str == '7+':
            # Example random choice for 7,8,9
            return np.random.choice([7, 8, 9], p=[0.7, 0.2, 0.1])
        return int(size_str)

    def _sample_earners(self, earner_dist):
        """
        Sample the number of earners from earner_dist. If '3+' is picked, pick between 3..5.
        """
        earners_key = np.random.choice(list(earner_dist.keys()), p=list(earner_dist.values()))
        if earners_key == '3+':
            # random int between 3 and 5
            return np.random.randint(3, 6)
        return int(earners_key)

