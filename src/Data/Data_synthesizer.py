from pathlib import Path
from src.component.data_part import IncomeDataProcessor
from src.component.data_part import IndividualIncomePredictor
from src.component.data_part import IncomeDataCleaner
import pandas as pd
import tabulate as tb

processor = IncomeDataProcessor()
income_data = pd.read_csv('cleaned_income_data.csv')
cleaner = IncomeDataCleaner()
cleaned_data = cleaner.fit_transform(income_data)
processor.fit(cleaned_data)
zipcode_stats = processor.zipcode_stats_
predictor = IndividualIncomePredictor(zipcode_stats)
customers = predictor.predict_individual(num_samples=1)

customers.to_csv('customers.csv', index=False)
print(customers[['zipcode', 'age_group', 'family_type', 'household_size', 'earners', 'income']].to_markdown(index=False))