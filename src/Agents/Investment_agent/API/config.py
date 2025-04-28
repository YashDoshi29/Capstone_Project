# config.py

# List of stock symbols to fetch data for.
STOCK_LIST = [
    'AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'JPM', 'GS', 'KO', 'PEP', 
          'XOM', 'NEE', 'CVX', 'WMT', 'HD', 'GME', 'TSLA', 'F', 'COIN', 'MRNA'
]

from datetime import datetime, timedelta

# Define time range: past 10 years
START_DATE = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")
