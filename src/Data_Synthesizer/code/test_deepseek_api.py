import requests
import json
from config import API_KEY

URL = "https://api.deepseek.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, can you echo back this test message?"}
    ],
    "temperature": 0.5,
    "max_tokens": 50
    # Removed "response_format" since it might not be supported by DeepSeek API
}

try:
    response = requests.post(URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()  # Will raise HTTPError for 4xx/5xx status codes
    data = response.json()
    print("Request succeeded! Response content:")
    print(json.dumps(data, indent=2))
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print("Response content:", response.text)
except requests.exceptions.RequestException as err:
    print(f"API request failed: {err}")