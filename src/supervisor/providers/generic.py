import json
from typing import Any, Dict, Optional

import aiohttp

from ..utils import DebouncedLogger
from .base import LLMProvider


class GenericProvider(LLMProvider):
    """Generic provider for LLM APIs."""

    def __init__(self, config: Dict[str, Any]):
        self.api_base = config.get("api_base", "http://localhost:1234/v1")
        self.model = config.get("model", "default-model")
        self.logger = DebouncedLogger(interval=5.0)
        self._sent_bytes = 0
        self._received_bytes = 0

    async def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
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

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30,
                ) as response:
                    self._received_bytes += len(await response.read())
                    response.raise_for_status()
                    result = await response.json()

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
