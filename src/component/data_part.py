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

            # Prepare distributions for the model
            age_dist = self._calculate_age_distribution(zip_data)
            family_dist = self._calculate_family_distribution(zip_data)
            earner_dist = self._calculate_earner_distribution(zip_data)
            size_dist = self._calculate_household_size(zip_data)

            # Build & fit the Bayesian model for this zipcode
            bayes_model = BayesianIncomeModel(
                draws=2500,
                tune=1500,
                cores=34,
                target_accept=0.9
            )
            bayes_model.fit(
                zip_data=zip_data,
                age_data=age_dist,
                family_data=family_dist,
                earner_data=earner_dist,
                size_data=size_dist
            )

            # Store results
            self.zipcode_stats_[zipcode] = {
                'age_dist': age_dist,
                'family_dist': family_dist,
                'earner_dist': earner_dist,
                'household_size_dist': size_dist,
                'bayesian_model': bayes_model
            }

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

class BayesianIncomeModel:
    def __init__(self,
                 draws=2500,
                 tune=1500,
                 cores=34,
                 target_accept=0.9):
        self.draws = draws
        self.tune = tune
        self.cores = cores
        self.target_accept = target_accept

    def fit(self, zip_data,
            age_data,
            family_data,
            earner_data,
            size_data):
        """
        zip_data: Pandas DataFrame subset for a single zipcode
        age_data, family_data, earner_data, size_data: dicts with
            'distribution' and 'incomes' or 'median_incomes'
        """
        observed_income = zip_data['Household Income'].values.astype(np.float64)

        # Convert dict distributions to arrays
        tiny = 1e-3
        age_probs = np.clip(
            np.array(list(age_data['distribution'].values()), dtype=np.float64),
            tiny, None
        )
        fam_probs = np.clip(
            np.array(list(family_data['distribution'].values()), dtype=np.float64),
            tiny, None
        )
        earn_probs = np.clip(
            np.array(list(earner_data['distribution'].values()), dtype=np.float64),
            tiny, None
        )
        size_probs = np.clip(
            np.array(list(size_data['distribution'].values()), dtype=np.float64),
            tiny, None
        )

        # Convert incomes
        age_mu_data = np.array(list(age_data['median_incomes'].values()), dtype=np.float64)
        fam_mu_data = np.array(list(family_data['incomes'].values()), dtype=np.float64)
        earn_mu_data = np.array(list(earner_data['incomes'].values()), dtype=np.float64)
        size_mu_data = np.array(list(size_data['incomes'].values()), dtype=np.float64)

        with pm.Model() as model:
            # Latent scaling for each distribution
            age_alpha = pm.Exponential('age_alpha', lam=1.0, shape=len(age_probs))
            fam_alpha = pm.Exponential('fam_alpha', lam=1.0, shape=len(fam_probs))
            earn_alpha = pm.Exponential('earn_alpha', lam=1.0, shape=len(earn_probs))
            size_alpha = pm.Exponential('size_alpha', lam=1.0, shape=len(size_probs))

            age_weights = pm.Dirichlet('age_weights', a=age_alpha * age_probs)
            fam_weights = pm.Dirichlet('fam_weights', a=fam_alpha * fam_probs)
            earn_weights = pm.Dirichlet('earn_weights', a=earn_alpha * earn_probs)
            size_weights = pm.Dirichlet('size_weights', a=size_alpha * size_probs)

            # Means for each category
            # (Here, we allow them to vary, but you could keep them fixed if you want.)
            age_mu = pm.Normal('age_mu', mu=age_mu_data, sigma=1e4, shape=len(age_mu_data))
            fam_mu = pm.Normal('fam_mu', mu=fam_mu_data, sigma=1e4, shape=len(fam_mu_data))
            earn_mu = pm.Normal('earn_mu', mu=earn_mu_data, sigma=1e4, shape=len(earn_mu_data))
            size_mu = pm.Normal('size_mu', mu=size_mu_data, sigma=1e4, shape=len(size_mu_data))

            # Weighted sum for final income
            mu_income = (
                pm.math.dot(age_weights, age_mu) +
                pm.math.dot(fam_weights, fam_mu) +
                pm.math.dot(earn_weights, earn_mu) +
                pm.math.dot(size_weights, size_mu)
            )

            sigma = pm.HalfNormal('sigma', sigma=1e5)

            # Example using Normal; you could also do StudentT or LogNormal
            pm.Normal('income', mu=mu_income, sigma=sigma, observed=observed_income)

            # Sample
            trace = pm.sample(
                draws=self.draws,
                tune=self.tune,
                cores=self.cores,
                target_accept=self.target_accept
            )

        self.model_ = model
        self.trace_ = trace
        return self

    def save_trace(self, path="my_trace.nc"):
        """Save the trace to a NetCDF file with ArviZ."""
        import arviz as az
        az.to_netcdf(self.trace_, path)
        print(f"Trace saved to {path}")

    def load_trace(self, path="my_trace.nc"):
        """Load the trace from disk."""
        import arviz as az
        self.trace_ = az.from_netcdf(path)
        print(f"Trace loaded from {path}")
        # Note: This returns an InferenceData object in PyMC>=4

    def get_trace(self):
        return self.trace_