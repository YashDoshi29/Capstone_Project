from pathlib import Path
import pandas as pd
import arviz as az
from src.component.customer import IncomeDataCleaner
from src.component.customer import AdvancedIncomeModel
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'cleaned_income_data.csv')
income_data = pd.read_csv(file_path)

model = AdvancedIncomeModel(epochs=50)
model.fit(income_data)
model.save("income_model.pkl")

synthetic_households = model.generate(1000)
print(synthetic_households.head())