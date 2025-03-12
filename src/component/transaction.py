import os
import numpy as np
import pandas as pd
import arviz as az
from datetime import datetime, timedelta

#####################################################################
# 1) CustomerSynthesizer:
#    - Loads posterior for each ZIP from .nc trace files
#    - For each new customer:
#       * pick a ZIP
#       * sample Income from that ZIP's posterior
#       * sample a Category usage distribution from that ZIP's posterior
#####################################################################
class CustomerSynthesizer:
    def __init__(self, trace_dir: str, categories: list):
        """
        :param trace_dir: Folder path containing .nc trace files.
                          e.g. "traces/trace_20037.nc"
        :param categories: List of all possible merchant categories.
                          e.g. ["Bakery", "Barber Shop", "Restaurant", ...]
        """
        self.trace_dir = trace_dir
        self.categories = categories
        self.traces = {}  # { zipcode: InferenceData } for quick lookup
        self._load_all_traces()

    def _load_all_traces(self):
        """Loads .nc files from trace_dir into memory."""
        for fname in os.listdir(self.trace_dir):
            if fname.endswith(".nc"):
                # e.g. trace_20037.nc => zipcode = "20037"
                zipcode = fname.replace("trace_", "").replace(".nc", "")
                path = os.path.join(self.trace_dir, fname)
                inference_data = az.from_netcdf(path)
                self.traces[zipcode] = inference_data
        print(f"Loaded {len(self.traces)} traces from {self.trace_dir}")

    def generate_customers(self, num_customers: int) -> pd.DataFrame:
        """
        Create synthetic customers, each with:
          - Zipcode (chosen from loaded traces)
          - Income (sampled from posterior)
          - Category usage distribution (Dirichlet-based from posterior)
          - Some additional fields (age, gender, household size) for realism
        Returns a DataFrame with columns:
          [Customer_ID, Zipcode, Age, Gender, Household_Size,
           Income, CategoryDist (list of floats for each category)]
        """
        # If no traces are loaded, fallback to random
        if not self.traces:
            print("No traces loaded; returning random customers.")
            return self._generate_random_customers(num_customers)

        # Let's pick a random ZIP (with equal probability) for each customer
        all_zipcodes = list(self.traces.keys())
        assigned_zips = np.random.choice(all_zipcodes, size=num_customers, replace=True)

        data_rows = []
        for i, zipcode in enumerate(assigned_zips, start=1):
            cust_id = f"DC_CUST_{i:06d}"

            # Sample posterior for this ZIP
            posterior = self.traces[zipcode].posterior  # xarray dataset

            # Flatten chain/draw dims
            # e.g. income_mu: (chain, draw)
            if "income_mu" in posterior and "income_sigma" in posterior:
                mu_vals = posterior["income_mu"].values.reshape(-1)     # shape ~ (total_draws,)
                sig_vals = posterior["income_sigma"].values.reshape(-1)
                idx = np.random.randint(0, len(mu_vals))
                mu = mu_vals[idx]
                sigma = sig_vals[idx]
                income = np.random.normal(mu, sigma)
                income = max(5000, income)  # clamp minimum
            else:
                # fallback if no income posterior present
                income = np.random.lognormal(mean=10, sigma=0.5)

            # Now for category usage distribution
            # Suppose there's a variable "category_weights" with shape=(num_categories,).
            if "category_weights" in posterior:
                cat_samples = posterior["category_weights"].values  # shape ~ (chain, draw, category)
                # Flatten chain/draw
                cat_samples = cat_samples.reshape(-1, cat_samples.shape[-1])  # e.g. (N, num_categories)
                # pick a random draw
                idx = np.random.randint(0, cat_samples.shape[0])
                cat_dist = cat_samples[idx, :]
                # ensure it sums to 1
                cat_dist = cat_dist / cat_dist.sum()
            else:
                # fallback: uniform
                cat_dist = np.ones(len(self.categories)) / len(self.categories)

            # random demographics
            age = np.random.randint(18, 85)
            gender = np.random.choice(["Male", "Female", "Other"], p=[0.48, 0.48, 0.04])
            hh_size = np.random.choice([1,2,3,4,5,6], p=[0.2,0.3,0.25,0.15,0.08,0.02])

            data_rows.append({
                "Customer_ID": cust_id,
                "Zipcode": zipcode,
                "Age": age,
                "Gender": gender,
                "Household_Size": hh_size,
                "Income": round(float(income), 2),
                # We'll store cat_dist as a list for usage later
                "CategoryDist": cat_dist.tolist()
            })

        return pd.DataFrame(data_rows)

    def _generate_random_customers(self, num_customers: int) -> pd.DataFrame:
        """
        Fallback if no real traces are found.
        Not used in normal operation, but you can keep it for safety.
        """
        df = pd.DataFrame({
            "Customer_ID": [f"DC_CUST_{i+1:06d}" for i in range(num_customers)],
            "Zipcode": np.random.choice(["00000"], size=num_customers),  # dummy
            "Age": np.random.randint(18, 85, size=num_customers),
            "Gender": np.random.choice(["Male", "Female", "Other"], size=num_customers),
            "Household_Size": np.random.randint(1,5, size=num_customers),
            "Income": np.round(np.random.lognormal(mean=10, sigma=0.5, size=num_customers), 2),
            "CategoryDist": [np.ones(len(self.categories))/len(self.categories)] * num_customers
        })
        return df


#####################################################################
# 2) TransactionSynthesizer:
#    - Takes customers w/ posterior-based "CategoryDist"
#    - For each spending event:
#        * picks a category from that distribution
#        * picks a merchant from that category
#          (optionally factoring in Zipcode or distance)
#        * picks a transaction amount/time
#####################################################################
class TransactionSynthesizer:
    def __init__(self, merchants_df: pd.DataFrame, categories: list):
        """
        :param merchants_df: DataFrame of merchants with columns:
             Merchant_ID, Business Name, Category, Zipcode, etc.
        :param categories: the same category list used in CustomerSynthesizer
        """
        self.merchants_df = merchants_df.copy()
        self.categories = categories

        # For convenience, group merchants by category
        self.merchants_by_cat = {}
        for cat in categories:
            df_cat = self.merchants_df[self.merchants_df["Category"] == cat]
            self.merchants_by_cat[cat] = df_cat

    def generate_transactions(self, customers_df: pd.DataFrame, weeks: int = 4) -> pd.DataFrame:
        """
        For each customer:
          - We'll interpret 'CategoryDist' as the probability distribution
            over categories for that person's day-to-day spending.
          - We generate a certain number of total transactions per week
            based on their income.
          - For each transaction:
             * draw a category from CategoryDist
             * pick a merchant in that category
             * pick a random amount/time
        """
        all_txns = []

        for _, cust in customers_df.iterrows():
            cust_id = cust["Customer_ID"]
            zipcode = str(cust["Zipcode"])
            income = cust["Income"]
            cat_dist = np.array(cust["CategoryDist"])  # shape = (len(categories),)

            # Let weekly budget be some fraction of monthly net:
            # e.g. monthly net ~ income*(1 - 0.2 tax) => weekly ~ /4
            monthly_net = income * (1 - 0.2)
            weekly_budget = monthly_net / 4
            # We'll do ~ (weekly_budget / 50) transactions per week
            # (Adjust as needed for more realism)
            transactions_per_week = max(1, int(weekly_budget // 50))

            for w in range(weeks):
                # For each transaction
                for _ in range(transactions_per_week):
                    # 1) pick category via cat_dist
                    cat_idx = np.random.choice(range(len(self.categories)), p=cat_dist)
                    category = self.categories[cat_idx]

                    # 2) pick a merchant from that category
                    merchants_cat = self.merchants_by_cat.get(category, None)
                    if merchants_cat is not None and not merchants_cat.empty:
                        merchant = merchants_cat.sample(1).iloc[0]
                    else:
                        # fallback if none in that category
                        merchant = {
                            "Merchant_ID": "NA",
                            "Business Name": "Misc Merchant",
                            "Category": category,
                            "Zipcode": zipcode
                        }

                    # 3) pick amount
                    # e.g. random up to 5% of weekly budget
                    amount = np.random.uniform(5, 0.05*weekly_budget)
                    timestamp = self._random_timestamp(week_index=w)

                    txn = {
                        "Customer_ID": cust_id,
                        "Zipcode": zipcode,
                        "Category": category,
                        "Merchant_ID": merchant.get("Merchant_ID", "NA"),
                        "Business_Name": merchant.get("Business Name", "Unknown"),
                        "Amount": round(amount, 2),
                        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    all_txns.append(txn)

        return pd.DataFrame(all_txns)

    def _random_timestamp(self, week_index: int) -> datetime:
        """
        Return a random datetime for the given 'week_index' offset
        from the current date.
        """
        now = datetime.now()
        # Subtract 'week_index' weeks
        base = now - timedelta(weeks=week_index)

        # Random day/hours in that week
        day_offset = np.random.randint(0, 7)
        hour = np.random.randint(7, 22)  # 7AM to 10PM
        minute = np.random.randint(0, 60)

        return base - timedelta(days=day_offset, hours=(24 - hour), minutes=minute)


#####################################################################
# 3) Example usage (main script)
#####################################################################
if __name__ == "__main__":
    # We'll use the categories you have in your merchant data
    ALL_CATEGORIES = [
        "Athletic Exhibition", "Auto Rental", "Auto Wash", "Bakery", "Barber Shop",
        "Beauty Booth", "Beauty Shop", "Beauty Shop Braiding", "Beauty Shop Electrology",
        "Beauty Shop Esthetics", "Beauty Shop Nails", "Bed and Breakfast",
        "Billiard Parlor", "Boarding House", "Bowling Alley", "Caterers", "Delicatessen",
        "Driving School", "Food Products", "Food Vending Machine", "Gasoline Dealer",
        "General Business Licenses", "Grocery Store", "Health Spa", "Hotel",
        "Ice Cream Manufacture", "Inn And Motel", "Marine Food Retail", "Massage Establishment",
        "Mobile Delicatessen", "Motion Picture Theatre", "Public Hall", "Restaurant",
        "Skating Rink", "Special Events", "Theater (Live)", "Tow Truck", "Tow Truck Business",
        "Tow Truck Storage Lot", "Vacation Rental"
    ]

    # 1) Create your CustomerSynthesizer from the Bayesian traces
    customer_synth = CustomerSynthesizer(trace_dir="traces", categories=ALL_CATEGORIES)

    # 2) Generate customers
    cust_df = customer_synth.generate_customers(num_customers=100)
    print("Sample of generated customers:\n", cust_df.head())

    # 3) Load your merchant dataset
    merchants_df = pd.read_csv("merchants.csv")  # must have "Category" matching the above

    # 4) Create the TransactionSynthesizer
    txn_synth = TransactionSynthesizer(merchants_df, ALL_CATEGORIES)

    # 5) Generate transactions for (e.g.) 4 weeks
    txn_df = txn_synth.generate_transactions(cust_df, weeks=4)
    print("Sample of generated transactions:\n", txn_df.head())

    # 6) Save them out
    cust_df.to_csv("synthetic_customers.csv", index=False)
    txn_df.to_csv("synthetic_transactions.csv", index=False)

    print("\nDone! Generated customers & transactions using posterior-based categories & incomes.")
