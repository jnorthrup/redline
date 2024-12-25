#!/usr/bin/env python3
import os
import json
import requests

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY environment variable not set")
    exit(1)

print(f"Using API key: {api_key[:5]}... (truncated)")
print("Sending request to OpenRouter...")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://github.com/redline",
    "X-Title": "Redline Greeting Test"
}

data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say hello!"}]
}

try:
    response = requests.post(
        "https://api.openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    print(f"\nStatus code: {response.status_code}")
    print("\nResponse headers:")
    print(json.dumps(dict(response.headers), indent=2))
    
    print("\nRaw response:")
    print(response.text)
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print("\nExtracted content:")
            print(content)
        else:
            print("\nNo content found in response")
    else:
        print(f"\nError: Received status code {response.status_code}")
        
except Exception as e:
    print(f"Error: {str(e)}")
