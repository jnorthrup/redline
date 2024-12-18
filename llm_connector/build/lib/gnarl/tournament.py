"""
Module for tournament-based LLM connector evaluation and comparison.

This module provides classes and methods for running tournaments between 
different Large Language Model (LLM) connectors, allowing for comparative 
analysis of their performance, cost, and response generation capabilities.
"""

from typing import List, Optional
from .interfaces import (
    AgentMemory, 
    Message, 
    ModelConfig, 
    LLMResponse, 
    StreamingLLMResponse, 
    LLMConnector
)


class TournamentModel:
    """
    Represents a tournament model for comparing different LLM connectors.

    This class manages a collection of LLM connectors and provides methods
    to run tournaments, generate responses, and calculate cost metrics.

    Attributes:
        connectors (List[LLMConnector]): List of LLM connectors to participate in the tournament.
    """

    def __init__(self, connectors: List[LLMConnector]):
        """
        Initialize the tournament model with a list of LLM connectors.

        Args:
            connectors (List[LLMConnector]): List of LLM connectors to compare.
        """
        self.connectors = connectors

    async def run_tournament(
        self,
        messages: List[Message],
        config: Optional[ModelConfig] = None,
        agent_memory: Optional[AgentMemory] = None,
    ) -> List[LLMResponse]:
        """
        Runs a tournament by generating responses from each connector and returning them.

        This method asynchronously generates responses from all connectors 
        using the same input messages and optional configuration.

        Args:
            messages (List[Message]): Conversation history and current prompt
            config (Optional[ModelConfig]): Optional configuration overrides
            agent_memory (Optional[AgentMemory]): Optional agent memory for tracking reasoning

        Returns:
            List[LLMResponse]: Responses from each connector
        """
        responses = []
        for connector in self.connectors:
            response = await connector.generate(messages, config, agent_memory)
            responses.append(response)
        return responses

    def calculate_cost_metrics(self, technical_debt: float, tokens: int) -> float:
        """
        Calculate cost metrics based on technical debt and token usage.

        This method provides a simple cost calculation that considers 
        technical debt and token consumption.

        Args:
            technical_debt (float): The technical debt score
            tokens (int): The number of tokens used

        Returns:
            float: The calculated cost metric, inversely proportional to token cube
        """
        return technical_debt / (tokens**3)


class TournamentLLMConnector(LLMConnector):
    """
    Abstract base class for LLM connectors that participate in a tournament.

    Provides a template for implementing LLM connectors with methods 
    for generating responses and validating configurations.
    """

    def __init__(self, config: ModelConfig):
        """
        Initialize the tournament LLM connector with a configuration.

        Args:
            config (ModelConfig): Configuration for the LLM connector.
        """
        self.config = config

    async def generate(
        self,
        messages: List[Message],
        config: Optional[ModelConfig] = None,
        agent_memory: Optional[AgentMemory] = None,
    ) -> LLMResponse:
        """
        Generate a response based on input messages.

        Args:
            messages (List[Message]): List of input messages.
            config (Optional[ModelConfig]): Optional configuration override.
            agent_memory (Optional[AgentMemory]): Optional agent memory.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate method")

    async def generate_stream(
        self,
        messages: List[Message],
        config: Optional[ModelConfig] = None,
        agent_memory: Optional[AgentMemory] = None,
    ) -> StreamingLLMResponse:
        """
        Generate a streaming response based on input messages.

        Args:
            messages (List[Message]): List of input messages.
            config (Optional[ModelConfig]): Optional configuration override.
            agent_memory (Optional[AgentMemory]): Optional agent memory.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_stream method")

    async def validate_config(self, config: ModelConfig) -> bool:
        """
        Validate the given configuration.

        Args:
            config (ModelConfig): Configuration to validate.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement validate_config method")
