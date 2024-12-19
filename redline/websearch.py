"""
Module for performing web searches.
"""

import os
import requests


class WebSearch:
    """Handles web search operations using external APIs."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def search(self, query):
        """
        Perform web search with given query.

        Args:
            query (str): Search terms

        Returns:
            dict: Search results
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": query},
            ],
        }
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is not set")

    web_search = WebSearch(api_key)
    query = "How many stars are there in our galaxy?"
    result = web_search.search(query)
    print(f"Search Result: {result['choices'][0]['message']['content']}")
