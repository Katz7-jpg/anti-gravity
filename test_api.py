import os
import requests
import json

api_key = "modalresearch_omx2pL-akvkXlBYAOAxiYwg--GbElAN84xMJhevcOrM"
base_url = "https://api.us-west-2.modal.direct/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "zai-org/GLM-5-FP8",
    "messages": [
        {"role": "user", "content": "Hello! Are you working?"}
    ]
}

try:
    response = requests.post(base_url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
