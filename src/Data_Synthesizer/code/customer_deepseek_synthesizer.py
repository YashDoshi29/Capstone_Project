import os
import sys
from config import API_KEY
# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.component.customer_deepseek import DeepSeekCustomerGenerator

# Rest of your code remains the same
script_dir = os.path.dirname(os.path.abspath(__file__))
INPUT_DATA = os.path.join(script_dir, 'cleaned_income_data.csv')
OUTPUT_FILE = "../data/synthetic_customers_deepseek.csv"

# Initialize and run generator
generator = DeepSeekCustomerGenerator(API_KEY)
generator.generate_customers(INPUT_DATA, OUTPUT_FILE)