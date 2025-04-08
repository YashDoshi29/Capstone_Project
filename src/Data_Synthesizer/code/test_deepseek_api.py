import requests
import json

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "age": 35,
        "gender": "Female",
        "household_size": 2,
        "income": 30000,
        "zipcode": "20001"
    }
)

print(json.dumps(response.json(), indent=2))