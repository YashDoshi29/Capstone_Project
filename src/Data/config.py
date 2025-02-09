# config.py

CENSUS_API_KEY = 'b9b3ecac3f95ad013778c6ca8f6854480be8f7c0'
DEEPSEEK_API_KEY = 'sk-20f42785068042f1b9d02719d2e22fc6'

CENSUS_API_ENDPOINT = "https://api.census.gov/data/2023/acs/acs5"
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# Mapping of states with FIPS codes and abbreviations.
STATES = {
    "DC": {"fips": "11", "abbr": "DC"},
    # Additional states can be added here.
}
