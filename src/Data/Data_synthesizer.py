from pathlib import Path
import pandas as pd
import arviz as az
from pathlib import Path
from src.component.customer import IncomeDataProcessor, IncomeDataCleaner
from src.component.customer import IndividualIncomePredictor

# 1) Clean and process the data
income_data = pd.read_csv('cleaned_income_data.csv')
cleaner = IncomeDataCleaner()
cleaned_data = cleaner.fit_transform(income_data)

processor = IncomeDataProcessor()
processor.fit(cleaned_data)  # This now trains the Bayesian models inside

zipcode_stats = processor.zipcode_stats_

# 2) Save Bayesian traces for each zipcode
Path("traces").mkdir(exist_ok=True)  # Ensure traces directory exists

for zipcode, stats in zipcode_stats.items():
    bayes_model = stats['bayesian_model']
    trace_path = f"traces/trace_{zipcode}.nc"
    az.to_netcdf(bayes_model.trace_, trace_path)
    print(f"Trace saved to {trace_path}")