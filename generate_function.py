"""Module for generating functions."""

import json
import logging
from typing import Optional

import requests

from redline.supervisor.generic_api_request import generic_api_request
from redline.supervisor.utils import format_bytes


def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
    """Generate a response using a generic API."""
    try:
        logging.debug("Sending request to generic API")
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False,
        }
        request_bytes = len(json.dumps(payload).encode("utf-8"))
        self.sent_bytes += request_bytes
        logging.debug("Bytes sent: %s", format_bytes(self.sent_bytes))
        response = generic_api_request(prompt, system_prompt)
        self.received_bytes += len(response.content)
        logging.debug(
            "Received response: %s, Bytes received: %s",
            response.status_code,
            format_bytes(self.received_bytes),
        )
        response.raise_for_status()
        result = response.json()
        logging.debug("Response JSON: %s", result)
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        return None
    except requests.Timeout:
        return None
    except requests.ConnectionError:
        return None
    except Exception as e:
        logging.error("An error occurred: %s", e)
        return None


logging.info("Message: %s", "static message")
