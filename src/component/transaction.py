import os
import numpy as np
import pandas as pd
import arviz as az
from datetime import datetime, timedelta


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
