"""Provider for Qwen API."""

import json
from typing import Any, Dict, Optional

import requests

from ..utils import DebouncedLogger, format_bytes
from .base import LLMProvider


class QwenProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.api_base = config.get("api_base", "http://localhost:1234/v1")
        self.model = config.get("model", "qwen-7b")
        self.logger = DebouncedLogger(interval=5.0)
        self._sent_bytes = 0
        self._received_bytes = 0

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False,
            }

            request_bytes = len(json.dumps(payload).encode("utf-8"))
            self._sent_bytes += request_bytes

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            self._received_bytes += len(response.content)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return None

    @property
    def sent_bytes(self) -> int:
        return self._sent_bytes

    @property
    def received_bytes(self) -> int:
        return self._received_bytes
