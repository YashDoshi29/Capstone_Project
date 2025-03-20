import pandas as pd
import numpy as np
from ctgan import CTGANSynthesizer
from geopy.distance import great_circle
from scipy.stats import lognorm
import random
from datetime import time, datetime, timedelta


class EnhancedTransactionGenerator:
    def __init__(self, merchant_df, real_transactions=None):
        self.merchant_df = merchant_df
        self.real_transactions = real_transactions
        self.ctgan = CTGANSynthesizer(epochs=150, batch_size=1000)
        self._preprocess_data()
        self._build_indices()

    def _preprocess_data(self):
        """Enrich merchant data with additional features"""
        # Add popularity weights if not present
        if 'popularity' not in self.merchant_df.columns:
            self.merchant_df['popularity'] = self._calculate_initial_popularity()

        # Add operating hours if not present
        if 'hours' not in self.merchant_df.columns:
            self.merchant_df['hours'] = self.merchant_df['category'].apply(
                self._default_operating_hours
            )

        # Create category amount distributions
        self.amount_params = self._create_amount_distributions()

    def _build_indices(self):
        """Create various lookup indices"""
        self.geo_index = self.merchant_df[['business_name', 'latitude', 'longitude']] \
            .dropna().set_index('business_name').apply(tuple, axis=1).to_dict()

        self.category_index = self.merchant_df.groupby('category')['business_name'] \
            .apply(list).to_dict()

        self.zip_category_map = self.merchant_df.groupby(['zipcode', 'category'])['business_name'] \
            .apply(list).to_dict()

    def _calculate_initial_popularity(self):
        """Calculate initial popularity based on category frequency"""
        category_counts = self.merchant_df['category'].value_counts(normalize=True)
        return self.merchant_df['category'].map(category_counts) * np.random.uniform(0.8, 1.2, len(self.merchant_df))

    def _default_operating_hours(self, category):
        """Assign default operating hours based on category"""
        hour_ranges = {
            'Restaurant': ('11:00-14:00', '17:00-22:00'),
            'Grocery Store': ('08:00-21:00',),
            'Hotel': ('00:00-23:59',),
            'Barber Shop': ('09:00-19:00',),
            'Gasoline Dealer': ('06:00-22:00',),
            # Add more category-specific defaults
        }
        return hour_ranges.get(category, ('10:00-20:00',))

    def _create_amount_distributions(self):
        """Define category-specific amount distributions"""
        return {
            'Restaurant': {'dist': 'lognorm', 'params': (0.5, 15, 100)},
            'Grocery Store': {'dist': 'lognorm', 'params': (0.6, 30, 150)},
            'Hotel': {'dist': 'lognorm', 'params': (0.4, 100, 400)},
            'Gasoline Dealer': {'dist': 'lognorm', 'params': (0.3, 20, 80)},
            # Add more categories
            'default': {'dist': 'lognorm', 'params': (0.5, 20, 200)}
        }

    def _generate_transaction_time(self, merchant):
        """Generate realistic transaction time within operating hours"""

        def parse_time(t_str):
            return datetime.strptime(t_str, '%H:%M').time()

        all_hours = []
        for period in merchant['hours']:
            start, end = period.split('-')
            all_hours.append((parse_time(start), parse_time(end)))

        # Select random operating period
        period = random.choice(all_hours)
        start_dt = datetime.combine(datetime.today(), period[0])
        end_dt = datetime.combine(datetime.today(), period[1])

        # Generate random time within period
        delta = (end_dt - start_dt).total_seconds()
        random_seconds = random.uniform(0, delta)
        return (start_dt + timedelta(seconds=random_seconds)).time()

    def _generate_transaction_amount(self, category):
        """Generate amount based on category distribution"""
        params = self.amount_params.get(category, self.amount_params['default'])
        if params['dist'] == 'lognorm':
            s, loc, scale = params['params']
            amount = lognorm.rvs(s, loc=loc, scale=scale)
            return round(float(amount), 2)
        return round(random.uniform(20, 200), 2)

    def _weighted_merchant_choice(self, candidates):
        """Select merchant based on popularity weights"""
        candidates_df = self.merchant_df[self.merchant_df['business_name'].isin(candidates)]
        weights = candidates_df['popularity'].values
        weights /= weights.sum()  # Normalize
        return np.random.choice(candidates_df['business_name'], p=weights)

    def generate_training_data(self):
        """Generate enhanced training data"""
        if self.real_transactions is not None:
            return self._augment_real_transactions()

        data = []
        for _ in range(50000):
            merchant = self.merchant_df.sample(1, weights='popularity').iloc[0]
            amount = self._generate_transaction_amount(merchant['category'])
            transaction_time = self._generate_transaction_time(merchant)

            data.append({
                'merchant': merchant['business_name'],
                'category': merchant['category'],
                'amount': amount,
                'zipcode': merchant['zipcode'],
                'time': transaction_time.strftime('%H:%M'),
                'online': int(merchant.get('online_available', False) and random.random() < 0.2)
            })

        return pd.DataFrame(data)

    def _augment_real_transactions(self):
        """Enrich real transaction data with additional features"""
        self.real_transactions['time'] = pd.to_datetime(self.real_transactions['timestamp']).dt.time
        merged = pd.merge(self.real_transactions, self.merchant_df,
                          left_on='merchant_id', right_on='business_id')

        # Add missing features
        merged['online'] = merged['channel'].apply(lambda x: 1 if x == 'online' else 0)
        return merged[['merchant', 'category', 'amount', 'zipcode', 'time', 'online']]

    def train_model(self):
        """Train with enhanced data"""
        training_data = self.generate_training_data()
        self.ctgan.fit(training_data,
                       discrete_columns=['merchant', 'category', 'zipcode', 'online', 'time'])

        # Update popularity weights based on training
        merchant_counts = training_data['merchant'].value_counts(normalize=True)
        self.merchant_df['popularity'] = self.merchant_df['business_name'].map(merchant_counts) \
            .fillna(self.merchant_df['popularity'] * 0.5)

    def generate_transactions(self, synthetic_households):
        """Generate fully realistic transactions"""
        transactions = []
        for _, household in synthetic_households.iterrows():
            zipcode = household['zipcode']
            num_tx = np.random.poisson(35)  # Average 35 transactions

            # Generate base transactions
            synth = self.ctgan.sample(num_tx,
                                      condition_column='zipcode',
                                      condition_value=zipcode)

            # Merchant validation and selection
            valid_tx = []
            for _, tx in synth.iterrows():
                try:
                    candidates = self._find_merchant_candidates(zipcode, tx['category'])
                    if candidates:
                        merchant = self._weighted_merchant_choice(candidates)
                        valid_tx.append({
                            'customer_id': household['customer_id'],
                            'date': self._generate_realistic_date(),
                            'merchant': merchant,
                            'category': tx['category'],
                            'amount': abs(tx['amount']),
                            'online': tx['online'],
                            'zipcode': zipcode
                        })
                except KeyError:
                    continue

            transactions.extend(valid_tx)

        return pd.DataFrame(transactions).drop_duplicates()

    def _find_merchant_candidates(self, zipcode, category):
        """Find valid merchants with geographic consistency"""
        # First try same zipcode
        candidates = self.zip_category_map.get((zipcode, category), [])

        # Then nearby zips within 3km
        if len(candidates) < 3:
            nearby_zips = self._find_nearby_zipcodes(zipcode, radius=3)
            for z in nearby_zips:
                candidates += self.zip_category_map.get((z, category), [])

        return list(set(candidates))

    def _find_nearby_zipcodes(self, target_zip, radius=3):
        """Find zipcodes within geographic radius"""
        target_loc = self.merchant_df[self.merchant_df['zipcode'] == target_zip] \
            [['latitude', 'longitude']].dropna().mean()

        nearby_zips = set()
        for _, row in self.merchant_df.iterrows():
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                dist = great_circle((target_loc['latitude'], target_loc['longitude']),
                                    (row['latitude'], row['longitude'])).km
                if dist <= radius:
                    nearby_zips.add(row['zipcode'])
        return list(nearby_zips)

    def _generate_realistic_date(self):
        """Generate date within realistic pattern (more recent dates more common)"""
        base_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)
        days = (end_date - base_date).days
        weighted_days = np.sqrt(np.random.uniform(0, days ** 2))
        return (base_date + timedelta(days=int(weighted_days))).strftime('%Y-%m-%d')


# Usage
if __name__ == "__main__":
    # Load data
    merchant_df = pd.read_csv('merchant_data.csv')
    try:
        real_transactions = pd.read_csv('real_transactions.csv')
    except FileNotFoundError:
        real_transactions = None

    # Initialize generator
    generator = EnhancedTransactionGenerator(merchant_df, real_transactions)

    # Train model
    generator.train_model()

    # Generate synthetic households
    synthetic_households = pd.DataFrame({
        'customer_id': range(1000),
        'zipcode': np.random.choice(merchant_df['zipcode'].unique(),
                                    size=1000,
                                    p=merchant_df['zipcode'].value_counts(normalize=True))
    })

    # Generate transactions
    transactions = generator.generate_transactions(synthetic_households)

    # Save results
    transactions.to_csv('enhanced_transactions.csv', index=False)