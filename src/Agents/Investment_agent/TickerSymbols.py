# import os
# import time
# import json
# from yahoo_fin import stock_info as si
# import yfinance as yf

# def build_ticker_company_mapping(max_tickers=1000, delay=1):
#     """
#     Fetches a mapping of tickers to company names from NASDAQ and S&P 500.
#     max_tickers: Maximum number of tickers to process.
#     delay: Seconds to wait between API calls to avoid rate limits.
#     """
#     nasdaq_tickers = si.tickers_nasdaq()   # Get NASDAQ tickers
#     sp500_tickers = si.tickers_sp500()       # Get S&P 500 tickers
#     # Combine the two lists and remove duplicates
#     tickers = list(set(nasdaq_tickers + sp500_tickers))
    
#     mapping = {}
#     count = 0
#     for ticker in tickers:
#         if count >= max_tickers:
#             break
#         try:
#             info = yf.Ticker(ticker).info
#             company_name = info.get("longName") or info.get("shortName")
#             if company_name:
#                 mapping[ticker] = company_name
#                 count += 1
#                 print(f"Fetched: {ticker} -> {company_name}")
#             else:
#                 print(f"No company name for {ticker}")
#         except Exception as e:
#             print(f"Error fetching {ticker}: {e}")
#         time.sleep(delay)
#     return mapping

# def save_mapping(mapping, filename):
#     with open(filename, "w") as f:
#         json.dump(mapping, f)
#     print(f"Mapping saved to {filename}")

# def load_mapping(filename):
#     with open(filename, "r") as f:
#         mapping = json.load(f)
#     return mapping

# if __name__ == "__main__":
#     mapping_file = "ticker_mapping.json"
#     # If the mapping file doesn't exist, build and save it
#     if not os.path.exists(mapping_file):
#         mapping = build_ticker_company_mapping(max_tickers=1000, delay=1)
#         save_mapping(mapping, mapping_file)
#     else:
#         mapping = load_mapping(mapping_file)
    
#     # Example: Print a few mapping entries
#     print("\nSample Ticker-Company Pairs:")
#     for ticker, company in list(mapping.items())[:10]:
#         print(f"{ticker}: {company}")

#-----------------------------------------------------------------------------------

# import json

# mapping_file = "ticker_mapping.json"  # Make sure this is the correct path to your file

# # Load the mapping from disk
# with open(mapping_file, "r") as f:
#     mapping = json.load(f)

# # Print the total count of mappings
# print(f"Total companies fetched: {len(mapping)}")

# # Print a few sample entries
# print("\nSample Ticker-Company Pairs:")
# for ticker, company in list(mapping.items())[:10]:
#     print(f"{ticker}: {company}")

#-----------------------------------------------------------------------------------

# from yahoo_fin import stock_info as si

# # Get tickers from each source
# nasdaq_tickers = si.tickers_nasdaq()         # NASDAQ-listed companies
# sp500_tickers = si.tickers_sp500()           # S&P 500 companies
# dow_tickers = si.tickers_dow()               # Dow Jones companies
# other_tickers = si.tickers_other() if hasattr(si, "tickers_other") else []

# # Print the counts for each group
# print("Number of NASDAQ companies:", len(nasdaq_tickers))
# print("Number of S&P 500 companies:", len(sp500_tickers))
# print("Number of Dow companies:", len(dow_tickers))
# print("Number of Other companies:", len(other_tickers))

#-----------------------------------------------------------------------------------


# import os
# import time
# import json
# from yahoo_fin import stock_info as si
# import yfinance as yf

# def build_ticker_company_mapping(delay=2.0):
#     """
#     Fetches a mapping of tickers to company names from NASDAQ, S&P 500, Dow, and Other markets.
#     This function processes tickers sequentially to avoid rate limiting.
#     """
#     # Fetch tickers from different sources
#     nasdaq_tickers = si.tickers_nasdaq()         # e.g., 4799 companies
#     sp500_tickers = si.tickers_sp500()           # e.g., 503 companies
#     dow_tickers = si.tickers_dow()               # e.g., 30 companies
#     other_tickers = si.tickers_other() if hasattr(si, "tickers_other") else []  # e.g., 6419 companies

#     # Combine and remove duplicates
#     all_tickers = list(set(nasdaq_tickers + sp500_tickers + dow_tickers + other_tickers))
#     print("Total tickers to process:", len(all_tickers))
    
#     mapping = {}
#     for ticker in all_tickers:
#         try:
#             # Fetch company info for this ticker
#             info = yf.Ticker(ticker).info
#             company_name = info.get("longName") or info.get("shortName")
#             if company_name:
#                 mapping[ticker] = company_name
#                 print(f"Fetched: {ticker} -> {company_name}")
#             else:
#                 print(f"No company name for ticker: {ticker}")
#         except Exception as e:
#             # Log the error and continue
#             print(f"Error fetching {ticker}: {e}")
#         time.sleep(delay)  # Pause to reduce rate-limit issues
#     return mapping

# if __name__ == "__main__":
#     # Build the complete mapping; delay of 1 second between requests
#     mapping = build_ticker_company_mapping(delay=1)
    
#     # Save the mapping to a JSON file so we don't have to re-fetch it each time
#     mapping_file = "ticker_mapping_full.json"
#     with open(mapping_file, "w") as f:
#         json.dump(mapping, f)
#     print(f"Mapping saved to {mapping_file} with total count: {len(mapping)}")

import os
import time
import json
from yahoo_fin import stock_info as si
import yfinance as yf

def is_valid_ticker(ticker):
    # Simple check: ticker should be non-empty and contain only alphanumerics (and possibly a period)
    return ticker and all(c.isalnum() or c == '.' for c in ticker)

def build_mapping_for_batch(tickers, delay=1):
    """
    Process a list of tickers sequentially.
    For each ticker, fetch its company info via yfinance and return a mapping (ticker -> company name).
    """
    mapping = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            company_name = info.get("longName") or info.get("shortName")
            if company_name:
                mapping[ticker] = company_name
                print(f"Fetched: {ticker} -> {company_name}")
            else:
                print(f"No company name for {ticker}")
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
        time.sleep(delay)  # Wait a bit to avoid rate limiting
    return mapping

def chunk_list(lst, chunk_size):
    """Yield successive chunks from list of size chunk_size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i+chunk_size]

def build_ticker_company_mapping_in_batches(delay=1, batch_size=1000):
    """
    Build a mapping of ticker symbols to company names in batches.
    This uses data from NASDAQ, S&P 500, Dow, and 'Other' tickers (if available).
    """
    # Get tickers from multiple sources
    nasdaq_tickers = si.tickers_nasdaq()
    sp500_tickers = si.tickers_sp500()
    dow_tickers = si.tickers_dow()
    other_tickers = si.tickers_other() if hasattr(si, "tickers_other") else []
    
    # Combine lists and remove duplicates
    all_tickers = list(set(nasdaq_tickers + sp500_tickers + dow_tickers + other_tickers))
    print("Total tickers to process:", len(all_tickers))
    
    # Filter out any tickers that don't look valid
    all_tickers = [ticker for ticker in all_tickers if is_valid_ticker(ticker)]
    print("Total valid tickers:", len(all_tickers))
    
    total_mapping = {}
    batch_number = 1
    for batch in chunk_list(all_tickers, batch_size):
        print(f"\nProcessing batch {batch_number} with {len(batch)} tickers...")
        batch_mapping = build_mapping_for_batch(batch, delay=delay)
        total_mapping.update(batch_mapping)
        print(f"Batch {batch_number} complete. Total fetched so far: {len(total_mapping)}")
        batch_number += 1
    return total_mapping

if __name__ == "__main__":
    # Build the complete mapping in batches.
    mapping = build_ticker_company_mapping_in_batches(delay=1, batch_size=1000)
    
    # Save the mapping to a JSON file so you don't have to re-fetch it each time.
    mapping_file = "ticker_mapping_full.json"
    with open(mapping_file, "w") as f:
        json.dump(mapping, f)
    print(f"Mapping saved to {mapping_file} with total count: {len(mapping)}")
