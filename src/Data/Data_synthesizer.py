from pathlib import Path
from src.component.data_part import IncomeDataProcessor
from src.component.data_part import IndividualIncomePredictor
from src.component.data_part import IncomeDataCleaner
import pandas as pd
import arviz as az

# 1) Clean and process the data
income_data = pd.read_csv('cleaned_income_data.csv')
cleaner = IncomeDataCleaner()
cleaned_data = cleaner.fit_transform(income_data)

processor = IncomeDataProcessor()
processor.fit(cleaned_data)  # This automatically trains Bayesian models for each zipcode

zipcode_stats = processor.zipcode_stats_

# 2) Save traces for all zipcodes (since they are already stored in processor.fit)
for zipcode, stats in zipcode_stats.items():
    trace_path = f"traces/trace_{zipcode}.nc"
    az.to_netcdf(stats['bayesian_model'].trace_, trace_path)
    print(f"Trace saved to {trace_path}")

