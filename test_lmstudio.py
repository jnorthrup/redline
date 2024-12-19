import requests
import os
import json

def test_lmstudio_connection():
    api_base = "http://localhost:1234/v1"  # Default LM Studio address
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        print(f"Attempting to connect to LM Studio at {api_base}/chat/completions")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error connecting to LM Studio: {str(e)}")

if __name__ == "__main__":
    test_lmstudio_connection()
