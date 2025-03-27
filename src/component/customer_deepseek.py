import os
import pandas as pd
import requests
import json
import random
import numpy as np
import time
from retrying import retry
from typing import Dict, List, Optional


class DeepSeekCustomerGenerator:
    """Generates synthetic customer profiles using DeepSeek's API"""

    def __init__(self, api_key: str):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limit_delay = 1.5  # Seconds between API calls

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def _api_request(self, payload: Dict) -> Optional[Dict]:
        """Make API request with retry logic"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return None

    def _build_prompt(self, row: Dict) -> str:
        """Construct the prompt for DeepSeek API"""
        return f"""Generate {int(row['Number Household'])} realistic customer profiles for zipcode {row['Zipcode']} with:
        - Age distribution: {self._format_age_distribution(row)}
        - Marital status: {self._marital_distribution(row)}
        - Household sizes: {self._household_distribution(row)}
        - Gender ratio: {self._gender_distribution(row)}
        - Earner distribution: {self._earner_distribution(row)}
        - Income distribution: {self._income_distribution(row)}

        Output JSON format:
        {{"customers": [
            {{
                "zipcode": "string",
                "age": int,
                "marital_status": "string", 
                "household_size": int,
                "income": float,
                "gender": "string",
                "earners": int
            }}
        ]}}"""

    def _format_age_distribution(self, row: Dict) -> str:
        brackets = [
            ('15-24', row['Number Household Income (15 to 24 years)']),
            ('25-44', row['Number Household Income (25 to 44 years)']),
            ('45-64', row['Number Household Income (45 to 64 years)']),
            ('65+', row['Number Household Income (65 years and over)'])
        ]
        return ", ".join([f"{b[0]}: {b[1]}" for b in brackets])

    def _marital_distribution(self, row: Dict) -> str:
        married = row['Number Families Married-couple families']
        single = row['Number Families Female householder, no spouse present'] + \
                 row['Number Families Male householder, no spouse present']
        return f"Married: {married}, Single: {single}"

    # Add similar methods for other distributions (_household_distribution, etc.)

    def _household_distribution(self, row: Dict) -> Dict:
        sizes = {
            '2': row['Number 2-person families'],
            '3': row['Number 3-person families'],
            '4': row['Number 4-person families'],
            '5': row['Number 5-person families'],
            '6': row['Number 6-person families'],
            '7+': row['Number 7-or-more person families']
        }
        total = sum(sizes.values())
        return {
            "type": "categorical",
            "categories": list(sizes.keys()),
            "probabilities": [v / total for v in sizes.values()]
        }

    def _gender_distribution(self, row: Dict) -> Dict:
        female = float(row['Number Families Female householder, no spouse present'])
        male = float(row['Number Families Male householder, no spouse present'])

        # Handle zero case
        if female + male == 0:
            return {
                "type": "categorical",
                "categories": ["female", "male"],
                "probabilities": [0.5, 0.5]  # Default equal distribution
            }

        return {
            "type": "categorical",
            "categories": ["female", "male"],
            "probabilities": [female / (female + male), male / (female + male)]
        }

    def _earner_distribution(self, row: Dict) -> Dict:
        earners = {
            '0': row['Number No earners'],
            '1': row['Number 1 earner'],
            '2': row['Number 2 earners'],
            '3+': row['Number 3 or more earners']
        }
        total = sum(earners.values())
        return {
            "type": "categorical",
            "categories": list(earners.keys()),
            "probabilities": [v / total for v in earners.values()]
        }

    def _income_distribution(self, row: Dict) -> Dict:
        # Calculate weighted average income across all categories
        total_income = sum(
            row[f'Household Income ({self._age_suffix(bracket)})'] * row[
                f'Number Household Income ({self._age_suffix(bracket)})']
            for bracket in ['15-24', '25-44', '45-64', '65+']
        )
        total_households = sum(
            row[f'Number Household Income ({self._age_suffix(bracket)})']
            for bracket in ['15-24', '25-44', '45-64', '65+']
        )
        avg_income = total_income / total_households if total_households else 50000
        return {
            "type": "normal",
            "mean": avg_income,
            "stddev": avg_income * 0.3,
            "min": 5000,
            "max": avg_income * 2.5
        }

    def _age_suffix(self, bracket: str) -> str:
        if '-' in bracket:
            return bracket.replace('-', ' to ') + ' years'
        return '65 years and over'

    def _process_response(self, response: Dict) -> List[Dict]:
        """Parse API response into customer records"""
        try:
            data = json.loads(response['choices'][0]['message']['content'])
            return data.get('customers', [])
        except:
            return []

    def generate_customers(self, input_file: str, output_file: str) -> None:
        """Main generation workflow"""
        raw_data = pd.read_csv(input_file)
        all_customers = []

        for _, row in raw_data.iterrows():
            try:
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a synthetic data generator that outputs accurate JSON."},
                        {"role": "user", "content": self._build_prompt(row.to_dict())}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }

                response = self._api_request(payload)
                if response:
                    customers = self._process_response(response)
                    all_customers.extend(customers)

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"Skipping zipcode {row.get('Zipcode', 'unknown')}: {str(e)}")
                continue

        df = pd.DataFrame(all_customers)
        df.to_csv(output_file, index=False)
        print(f"Successfully generated {len(df)} customer profiles")

    @staticmethod
    def _validate_row(row: Dict) -> bool:
        """Ensure required columns exist"""
        required = [
            'Zipcode',
            # Age distribution columns
            'Number Household Income (15 to 24 years)',
            'Household Income (15 to 24 years)',
            'Number Household Income (25 to 44 years)',
            'Household Income (25 to 44 years)',
            'Number Household Income (45 to 64 years)',
            'Household Income (45 to 64 years)',
            'Number Household Income (65 years and over)',
            'Household Income (65 years and over)',
            # Family structure columns
            'Number Families Married-couple families',
            'Income Families Married-couple families',
            'Number Families Female householder, no spouse present',
            'Income Families Female householder, no spouse present',
            'Number Families Male householder, no spouse present',
            'Income Families Male householder, no spouse present',
            # Earner columns
            'Number No earners', 'Income No earners',
            'Number 1 earner', 'Income 1 earner',
            'Number 2 earners', 'Income 2 earners',
            'Number 3 or more earners', 'Income 3 or more earners',
            # Household size columns
            'Number 2-person families', 'Income 2-person families',
            'Number 3-person families', 'Income 3-person families',
            'Number 4-person families', 'Income 4-person families',
            'Number 5-person families', 'Income 5-person families',
            'Number 6-person families', 'Income 6-person families',
            'Number 7-or-more person families', 'Income 7-or-more person families'
        ]
        return all(col in row for col in required)
