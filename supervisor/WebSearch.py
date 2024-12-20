import os
import subprocess
import sys

import requests
from openai import OpenAI

from redline.supervisor.utils import DebouncedLogger


class WebSearch:
    def __init__(self, api_key: str = None):
        if api_key is None:
            if len(sys.argv) > 1:
                self.api_key = sys.argv[1]
            else:
                raise ValueError(
                    "API key must be provided as a command line argument or passed to the constructor"
                )
        else:
            self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.logger = DebouncedLogger(interval=5.0)
        self.logger.debug(f"WebSearch initialized with API key: {self.api_key}")
        self.sent_bytes = 0
        self.received_bytes = 0

    def search(self, query: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant and you need to "
                    "engage in a helpful, detailed, polite conversation with a user."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        # Chat completion without streaming
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
        )
        print(response)

        # Chat completion with streaming
        response_stream = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
            stream=True,
        )
        for response in response_stream:
            print(response)

        return response


import json

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Perform a web search.")
    parser.add_argument("api_key", type=str, help="The API key for Perplexity AI.")
    parser.add_argument("query", type=str, help="The search query.")

    args = parser.parse_args()

    ws = WebSearch(api_key=args.api_key)
    ws.search(args.query)
