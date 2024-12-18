"""
LLMConnectorHelper for interacting with Large Language Models.
"""

import typing  # Fixed import order
from typing import List
from .metrics_helper import MetricsHelper
from .interfaces import Message, LLMResponse

class LLMConnectorHelper:
    """
    Helper class for LLM Connector functionalities.
    """
    def __init__(self, config):
        # Initialize LLM connector with configuration
        self.config = config
        self.metrics_helper = MetricsHelper()
        # TODO 
    
    @MetricsHelper.async_metrics_decorator
    async def interact_with_llm(self, prompt: str) -> LLMResponse:
        """
        Asynchronously interact with the LLM using a prompt.
        """
        self.metrics_helper.record_exec_start()
        try:
            response = await self.send_prompt(prompt)
            self.metrics_helper.record_exec_end(success=True)
            return response
        except Exception as e:
            self.metrics_helper.record_exec_end(success=False, error=str(e))
            raise e
    
    @MetricsHelper.async_metrics_decorator
    async def generate_response(self, messages: List[Message]) -> LLMResponse:
        """
        Asynchronously generate a response based on message history.
        """
        combined_prompt = self.combine_messages(messages)
        self.metrics_helper.record_exec_start()
        try:
            response = await self.send_prompt(combined_prompt)
            self.metrics_helper.record_exec_end(success=True)
            return response
        except Exception as e:
            self.metrics_helper.record_exec_end(success=False, error=str(e))
            raise e
    
    async def send_prompt(self, prompt: str) -> LLMResponse:
        """
        Send a prompt to the LLM.

        Args:
            prompt (str): The prompt to send.

        Returns:
            Response from the LLM.
        """
        # ...implementation...

    def combine_messages(self, messages: List[Message]) -> str:
        """
        Combine multiple messages into a single prompt.

        Args:
            messages (List[Message]): List of message objects.

        Returns:
            str: Combined prompt string.
        """
        combined = "\n".join([msg.content for msg in messages])
        return combined
        return combined

    async def some_async_method(self):
        # TODO 
        pass

    # ...other methods related to LLM interaction...

    async def some_async_method(self):
        # TODO 
        pass

    # ...other methods related to LLM interaction...