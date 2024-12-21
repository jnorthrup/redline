"""
Module for web search functionality.
"""

import requests
from typing import Any, Dict, List, Optional

from .utils import DebouncedLogger


class WebSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = DebouncedLogger(interval=5.0)
        self.base_url = "https://api.duckduckgo.com"

    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform a web search and return the results."""
        try:
            params = {
                "q": query,
                "format": "json",
                "pretty": 1
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            self.logger.debug(f"Web search results for query: {query}")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error during web search: {e}")
            return None
