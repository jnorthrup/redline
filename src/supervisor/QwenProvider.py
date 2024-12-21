"""Module for GenericProvider."""

from datetime import datetime
from typing import Any, Dict, Optional

from openai import OpenAI

from .utils import DebouncedLogger


class GenericProvider:
    """Class for GenericProvider."""

    def __init__(self, config: Dict[str, Any]):
        try:
            self.config = config
            self.api_base = config.get("api_base")
            self.model = config.get("model")
            self.logger = DebouncedLogger(interval=5.0)
            self.logger.debug(f"GenericProvider initialized with config: {self.config}")
            self._sent_bytes = 0
            self._received_bytes = 0
            self.client = OpenAI(api_key="not-needed", base_url=self.api_base)
        except Exception as e:
            self.logger.error(f"Error initializing GenericProvider: {e}")
            raise

    async def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Generate text based on the given prompts."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            self.logger.debug(
                f"Sending request to {self.api_base} with model {self.model}"
            )
            print(f"Sending request to {self.api_base} with model {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            self._sent_bytes += len(str(messages))
            self._received_bytes += len(str(response))

            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error during text generation: {e}")
            return None

    @property
    def sent_bytes(self) -> int:
        """Get the number of sent bytes."""
        return self._sent_bytes

    @property
    def received_bytes(self) -> int:
        """Get the number of received bytes."""
        return self._received_bytes
