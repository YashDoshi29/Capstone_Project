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
        # Get your computed distributions & incomes
        age_data = self._calculate_age_distribution(zip_data)
        family_data = self._calculate_family_distribution(zip_data)
        earner_data = self._calculate_earner_distribution(zip_data)
        size_data = self._calculate_household_size(zip_data)

        # Example: If zip_data['Household Income'] has multiple rows, collect them into a 1D numpy array.
        # If you truly only have one row, it’s still fine, but a single data point won’t let the model learn very much!
        observed_income = zip_data['Household Income'].values.astype(np.float64)

        # Fetch raw probabilities (dict) and incomes
        age_probs_data = np.array(list(age_data['distribution'].values()), dtype=np.float64)
        family_probs_data = np.array(list(family_data['distribution'].values()), dtype=np.float64)
        earner_probs_data = np.array(list(earner_data['distribution'].values()), dtype=np.float64)
        size_probs_data = np.array(list(size_data['distribution'].values()), dtype=np.float64)

        # Convert incomes to float arrays
        age_mu_data = np.array(list(age_data['median_incomes'].values()), dtype=np.float64)
        family_mu_data = np.array(list(family_data['incomes'].values()), dtype=np.float64)
        earner_mu_data = np.array(list(earner_data['incomes'].values()), dtype=np.float64)
        size_mu_data = np.array(list(size_data['incomes'].values()), dtype=np.float64)

        # A small constant to avoid zeros in the Dirichlet
        tiny = 1e-3
        age_probs_data = np.clip(age_probs_data, tiny, None)
        family_probs_data = np.clip(family_probs_data, tiny, None)
        earner_probs_data = np.clip(earner_probs_data, tiny, None)
        size_probs_data = np.clip(size_probs_data, tiny, None)

        with pm.Model() as income_model:
            # Instead of forcing the Dirichlet's a=... to the distribution from the dictionary,
            # we can treat that distribution as a baseline "shape" but scale it by latent alpha parameters
            # so that the model can deviate from your prior if the data suggests otherwise.
            # E.g., Dirichlet(a = alpha * baseline_probs).
            age_alpha = pm.Exponential('age_alpha', lam=1.0, shape=len(age_probs_data))
            family_alpha = pm.Exponential('family_alpha', lam=1.0, shape=len(family_probs_data))
            earner_alpha = pm.Exponential('earner_alpha', lam=1.0, shape=len(earner_probs_data))
            size_alpha = pm.Exponential('size_alpha', lam=1.0, shape=len(size_probs_data))

            age_weights = pm.Dirichlet('age_weights', a=age_alpha * age_probs_data)
            family_weights = pm.Dirichlet('family_weights', a=family_alpha * family_probs_data)
            earner_weights = pm.Dirichlet('earner_weights', a=earner_alpha * earner_probs_data)
            size_weights = pm.Dirichlet('size_weights', a=size_alpha * size_probs_data)

            # If you also want to *learn* each category’s average income rather than treat them as fixed,
            # you can put priors on them.  Otherwise, you can keep them fixed from your dictionary.
            # Example of placing Normal priors around your dictionary’s median incomes:
            age_mu = pm.Normal('age_mu',
                               mu=age_mu_data,
                               sigma=1e4,
                               shape=len(age_mu_data))  # shape must match # categories
            family_mu = pm.Normal('family_mu',
                                  mu=family_mu_data,
                                  sigma=1e4,
                                  shape=len(family_mu_data))
            earner_mu = pm.Normal('earner_mu',
                                  mu=earner_mu_data,
                                  sigma=1e4,
                                  shape=len(earner_mu_data))
            size_mu = pm.Normal('size_mu',
                                mu=size_mu_data,
                                sigma=1e4,
                                shape=len(size_mu_data))

            # Weighted sum of each category’s mean
            mu_income = (
                    pm.math.dot(age_weights, age_mu) +
                    pm.math.dot(family_weights, family_mu) +
                    pm.math.dot(earner_weights, earner_mu) +
                    pm.math.dot(size_weights, size_mu)
            )

            # Prior for scale
            sigma = pm.HalfNormal('sigma', sigma=1e5)

            # If you expect heavy tails or skew, you could do:
            #   nu = pm.Exponential('nu', 1/30.)
            #   pm.StudentT('income', nu=nu, mu=mu_income, sigma=sigma, observed=observed_income)
            # Otherwise, you can keep pm.Normal. Another common approach is pm.Lognormal.
            pm.Normal('income', mu=mu_income, sigma=sigma, observed=observed_income)

            trace = pm.sample(
                draws=3000,  # Increase draws
                tune=2000,  # Increase tuning
                cores=32,  # Possibly more cores if you have them
                target_accept=0.9  # Higher target accept can improve mixing
            )

        return {
            'model': income_model,
            'trace': trace,
            # Return the arrays or random variables as needed
            'age_mu': age_mu_data,  # or age_mu if learned
            'family_mu': family_mu_data,  # or family_mu if learned
            'earner_mu': earner_mu_data,  # or earner_mu if learned
            'size_mu': size_mu_data  # or size_mu if learned
        }


class IndividualIncomePredictor:
    """Predict individual income using Bayesian posterior weights from zipcode-level models"""

    def __init__(self, zipcode_stats):
        self.zipcode_stats = zipcode_stats

    def predict_individual(self, num_samples=1):
        """Generate synthetic individuals with Bayesian-weighted incomes"""
        individuals = []

        for zipcode, stats in self.zipcode_stats.items():
            for _ in range(num_samples):
                demographics = self._sample_demographics(
                    zipcode,
                    stats['age_dist']['distribution'],
                    stats['family_dist']['distribution'],
                    stats['earner_dist']['distribution'],
                    stats['household_size_dist']['distribution']
                )

                income = self._calculate_bayesian_income(demographics)
                individuals.append({**demographics, 'income': income})

        return pd.DataFrame(individuals)

    def _sample_demographics(self, zipcode, age_dist, family_dist, earner_dist, size_dist):
        """Sample demographics with proper type handling"""
        return {
            'zipcode': zipcode,
            'age_group': self._safe_choice(age_dist),
            'family_type': self._safe_choice(family_dist),
            'earners': self._sample_earners(earner_dist),
            'household_size': self._parse_household_size(
                self._safe_choice(size_dist)
            )
        }

    def _calculate_bayesian_income(self, demographics):
        """Calculate income using posterior weights and demographic medians"""
        zipcode = demographics['zipcode']
        stats = self.zipcode_stats[zipcode]
        model_data = stats['income_model']

        # Get posterior sample weights
        weights = self._get_posterior_weights(zipcode)

        # Get indices for each demographic category
        age_idx = self._get_category_index(stats['age_dist'], 'age_group', demographics)
        family_idx = self._get_category_index(stats['family_dist'], 'family_type', demographics)
        earner_idx = self._get_earner_index(stats['earner_dist'], demographics)
        size_idx = self._get_size_index(stats['household_size_dist'], demographics)

        # Calculate weighted components
        return (
                weights['age'][age_idx] * model_data['age_mu'][age_idx] +
                weights['family'][family_idx] * model_data['family_mu'][family_idx] +
                weights['earner'][earner_idx] * model_data['earner_mu'][earner_idx] +
                weights['size'][size_idx] * model_data['size_mu'][size_idx]
        )

    def _get_posterior_weights(self, zipcode):
        """Sample weights from Bayesian posterior"""
        trace = self.zipcode_stats[zipcode]['income_model']['trace']
        idx = np.random.randint(len(trace))
        return {
            'age': trace['age_weights'][idx],
            'family': trace['family_weights'][idx],
            'earner': trace['earner_weights'][idx],
            'size': trace['size_weights'][idx]
        }

    def _get_category_index(self, dist_data, key, demographics):
        """Get index position for a demographic category"""
        categories = list(dist_data['distribution'].keys())
        return categories.index(demographics[key])

    def _get_earner_index(self, dist_data, demographics):
        """Handle 3+ earner conversion"""
        earners = list(dist_data['distribution'].keys())
        earner_key = '3+' if demographics['earners'] >= 3 else str(demographics['earners'])
        return earners.index(earner_key)

    def _get_size_index(self, dist_data, demographics):
        """Handle household size conversion"""
        sizes = list(dist_data['distribution'].keys())
        size = demographics['household_size']
        size_key = '7+' if (isinstance(size, int) and size >= 7) else str(size)
        return sizes.index(size_key)

    def _safe_choice(self, dist):
        """Numerically stable category sampling"""
        probs = np.array(list(dist.values()), dtype=np.float64)
        probs += 1e-8  # Add tiny epsilon to avoid zeros
        probs /= probs.sum()
        return np.random.choice(list(dist.keys()), p=probs)

    def _sample_earners(self, dist):
        """Sample earners with proper 3+ handling"""
        key = self._safe_choice(dist)
        return np.random.randint(3, 6) if key == '3+' else int(key)

    def _parse_household_size(self, size_str):
        """Convert size strings to numerical values"""
        if size_str == '7+':
            return np.random.choice([7, 8, 9], p=[0.7, 0.2, 0.1])
        return int(size_str)

