"""
Module for generating responses using the Qwen API.
"""

import json
import logging
import requests
from typing import Optional

def format_bytes(size: int) -> str:
    power = 2**10
    n = 0
    power_labels = {0: 'bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
    """Generate a response from the Qwen API."""
    try:
        logging.debug("Sending request to Qwen API: %s", self.api_base)
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }
        request_bytes = len(json.dumps(payload).encode('utf-8'))
        self.sent_bytes += request_bytes
        logging.debug("Qwen Bytes sent: %s", format_bytes(self.sent_bytes))
        response = requests.post(self.api_base, headers=headers, json=payload, timeout=30)
        self.received_bytes += len(response.content)
        logging.debug("Qwen Received response: %s, Bytes received: %s", response.status_code, format_bytes(self.received_bytes))
        response.raise_for_status()
        result = response.json()
        logging.debug("Qwen response JSON: %s", result)
        if 'choices' in result and result['choices']:
            return result['choices'][0]['message']['content']
        return None
    except requests.Timeout:
        return None
    except requests.ConnectionError:
        return None
    except Exception as e:
        logging.error("An error occurred: %s", e)
        return None
