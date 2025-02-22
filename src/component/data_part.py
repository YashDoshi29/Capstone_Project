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

    def remove_unwanted_columns(self, df):
        for key, keyword in self.keywords.items():
            df = df.loc[:, ~df.columns.str.contains(keyword, case=False, na=False)]
        return df

    def rename_columns(self, df):
        new_columns = []
        for col in df.columns:
            for phrase, replacement in self.common_phrases.items():
                if phrase in col:
                    col = col.replace(phrase, replacement).strip()
                    if replacement.startswith("Household Income ("):
                        col += ")"
            new_columns.append(col)
        df.columns = new_columns
        return df

    def clean_csv_columns(self, data_path, output_path):
        df = pd.read_csv(data_path)
        df = self.remove_unwanted_columns(df)
        df = self.rename_columns(df)
        df.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")

#Customer data synthesizer

class IncomeDataProcessor(BaseEstimator, TransformerMixin):
    """Advanced processor for census-style income data"""

    def __init__(self):
        self.age_brackets = [
            '15-24', '25-44', '45-64', '65+'
        ]
        self.family_columns = [
            'Married-couple families',
            'Female householder',
            'Male householder'
        ]

    def fit(self, X, y=None):
        # Calculate zipcode-level distributions
        self.zipcode_stats_ = {}
        for zipcode in X['Zipcode'].unique():
            zip_data = X[X['Zipcode'] == zipcode]

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

    def _calculate_age_distribution(self, zip_data):
        """Calculate age probability distribution using household counts"""
        age_bracket_map = {
            '15-24': '15 to 24 years',
            '25-44': '25 to 44 years',
            '45-64': '45 to 64 years',
            '65+': '65 years and over'
        }

        # Get household counts for each age bracket
        household_counts = {
            bracket: zip_data[f'Number Household Income ({age_bracket_map[bracket]})'].values[0]
            for bracket in self.age_brackets
        }

        total_households = sum(household_counts.values())

        return {
            'distribution': {
                bracket: count / total_households
                for bracket, count in household_counts.items()
            },
            'median_incomes': {
                bracket: zip_data[f'Household Income ({age_bracket_map[bracket]})'].values[0]
                for bracket in self.age_brackets
            }
        }

    def _calculate_family_distribution(self, zip_data):
        """Calculate family structure with income data"""
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
            'incomes': {
                k: zip_data[v['income_col']].values[0]
                for k, v in family_types.items()
            }
        }

    def _calculate_earner_distribution(self, zip_data):
        """Calculate earner distribution with income data"""
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
            'incomes': {
                k: zip_data[v['income_col']].values[0]
                for k, v in earner_types.items()
            }
        }

    def _calculate_household_size(self, zip_data):
        """Calculate household size distribution with income data"""
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
            'incomes': {
                k: zip_data[v['income_col']].values[0]
                for k, v in sizes.items()
            }
        }

    def _build_bayesian_model(self, zip_data):
        """Integrated hierarchical model with multiple demographic factors"""
        # Get all demographic data
        age_data = self._calculate_age_distribution(zip_data)
        family_data = self._calculate_family_distribution(zip_data)
        earner_data = self._calculate_earner_distribution(zip_data)
        size_data = self._calculate_household_size(zip_data)

        with pm.Model() as income_model:
            # Demographic weights (Dirichlet priors)
            age_weights = pm.Dirichlet('age_weights',
                                       a=list(age_data['distribution'].values()))
            family_weights = pm.Dirichlet('family_weights',
                                          a=list(family_data['distribution'].values()))
            earner_weights = pm.Dirichlet('earner_weights',
                                          a=list(earner_data['distribution'].values()))
            size_weights = pm.Dirichlet('size_weights',
                                        a=list(size_data['distribution'].values()))

            # Baseline incomes from observed medians
            age_mu = pm.ConstantData('age_mu', list(age_data['median_incomes'].values()))
            family_mu = pm.ConstantData('family_mu', list(family_data['incomes'].values()))
            earner_mu = pm.ConstantData('earner_mu', list(earner_data['incomes'].values()))
            size_mu = pm.ConstantData('size_mu', list(size_data['incomes'].values()))

            # Combined income expectation
            mu_income = (
                    pm.math.dot(age_weights, age_mu) +
                    pm.math.dot(family_weights, family_mu) +
                    pm.math.dot(earner_weights, earner_mu) +
                    pm.math.dot(size_weights, size_mu)
            )

            # Error term
            sigma = pm.HalfNormal('sigma', sigma=1e5)

            # Likelihood
            income = pm.Normal('income',
                               mu=mu_income,
                               sigma=sigma,
                               observed=zip_data['Household Income'])

        return income_model


class IndividualIncomePredictor:
    """Predict individual income using zipcode-level statistics with full demographic integration"""

    def __init__(self, zipcode_stats):
        self.zipcode_stats = zipcode_stats

    def predict_individual(self, num_samples=1000):
        """Generate synthetic individuals with full demographic integration"""
        individuals = []

        for zipcode, stats in self.zipcode_stats.items():
            # Get all demographic distributions and incomes
            age_data = stats['age_dist']
            family_data = stats['family_dist']
            earner_data = stats['earner_dist']
            size_data = stats['household_size_dist']

            for _ in range(num_samples):
                # 1. Sample demographic characteristics
                demographics = self._sample_demographics(
                    age_data,
                    family_data,
                    earner_data,
                    size_data
                )

                # 2. Calculate base income from demographic medians
                base_income = self._calculate_base_income(demographics)

                # 3. Apply realistic adjustments
                final_income = self._apply_realistic_adjustments(base_income, demographics)

                individuals.append({
                    'zipcode': zipcode,
                    **demographics,
                    'income': final_income
                })

        return pd.DataFrame(individuals)

    def _sample_demographics(self, age_data, family_data, earner_data, size_data):
        """Sample individual characteristics using demographic distributions"""
        return {
            'age_group': np.random.choice(
                list(age_data['distribution'].keys()),
                p=list(age_data['distribution'].values())
            ),
            'family_type': np.random.choice(
                list(family_data['distribution'].keys()),
                p=list(family_data['distribution'].values())
            ),
            'earners': self._sample_earners(earner_data['distribution']),
            'household_size': np.random.choice(
                list(size_data['distribution'].keys()),
                p=list(size_data['distribution'].values())
            )
        }

    def _calculate_base_income(self, demographics):
        """Calculate base income using demographic-specific medians"""
        # Get median references from zipcode data
        age_median = self.zipcode_stats[demographics['zipcode']]['age_dist']['median_incomes'][
            demographics['age_group']]
        family_median = self.zipcode_stats[demographics['zipcode']]['family_dist']['incomes'][
            demographics['family_type']]
        earner_median = self.zipcode_stats[demographics['zipcode']]['earner_dist']['incomes'][
            str(demographics['earners'])]
        size_median = self.zipcode_stats[demographics['zipcode']]['household_size_dist']['incomes'][
            demographics['household_size']]

        # Bayesian-weighted combination
        return 0.4 * age_median + 0.3 * family_median + 0.2 * earner_median + 0.1 * size_median

    def _apply_realistic_adjustments(self, base_income, demographics):
        """Apply economic reality checks and adjustments"""
        # 1. Household size adjustment (economies of scale)
        size_factor = 1 / (int(demographics['household_size']) ** 0.15)

        # 2. Earner productivity multiplier
        if demographics['earners'] == 0:
            return 0  # Non-earning household
        earner_factor = 1 + 0.18 * (demographics['earners'] - 1)

        # 3. Family structure multiplier
        family_multiplier = {
            'married': 1.15,
            'female_head': 1.05,
            'male_head': 1.07
        }[demographics['family_type']]

        # 4. Log-normal variation (σ=0.1 preserves median)
        varied_income = base_income * size_factor * earner_factor * family_multiplier
        varied_income *= np.random.lognormal(0, 0.1)

        return max(varied_income, 15000)  # Poverty line floor

    def _sample_earners(self, earner_dist):
        """Convert earner distribution to integer counts"""
        earners = np.random.choice(
            list(earner_dist.keys()),
            p=list(earner_dist.values())
        )
        if earners == '3+':
            return np.random.randint(3, 6)  # Realistic upper bound
        return int(earners)