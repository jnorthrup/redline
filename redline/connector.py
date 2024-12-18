"""
Module for base LLM connector implementations and related utility classes.

This module provides base classes and interfaces for LLM (Large Language Model)
connectors, response handling, and agent memory management.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from .interfaces import (AgentMemory, LLMConnector, LLMResponse, Message,
                         ModelConfig, StreamingLLMResponse)


class BaseLLMConnector(LLMConnector):
    """
    Base class for LLM connectors.

    Provides a template for implementing LLM connector classes with
    methods for generating responses and validating configurations.
    """

    def __init__(self, config: ModelConfig):
        """
        Initialize the base LLM connector with a configuration.

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

    def get_connector_info(self) -> Dict[str, Any]:
        """
        Provide additional information about the connector.

        Returns:
            Dict[str, Any]: A dictionary with connector metadata.
        """
        return {"config": self.config}

    def get_supported_features(self) -> List[str]:
        """
        Get a list of supported features for this connector.

        Returns:
            List[str]: A list of supported features.
        """
        return ["generate", "generate_stream", "config_validation"]


class SimpleAgentMemory(AgentMemory):
    """
    Simple implementation of AgentMemory protocol.

    Provides basic methods for storing and retrieving reasoning steps.
    """

    def __init__(self):
        """
        Initialize the SimpleAgentMemory with an empty list of reasoning steps.
        """
        self.reasoning_steps: List[Message] = []
        self.bias: Optional[str] = None

    def store_reasoning_step(self, message: Message) -> None:
        """
        Store a reasoning step.

        Args:
            message (Message): The reasoning step to store.
        """
        self.reasoning_steps.append(message)

    def get_reasoning_history(
        self, limit: Optional[int] = None, filter_fn: Optional[callable] = None
    ) -> List[Message]:
        """
        Retrieve reasoning history.

        Args:
            limit (Optional[int], optional): Optional limit on number of steps to return.
            filter_fn (Optional[callable], optional): Optional function to filter reasoning steps.

        Returns:
            List[Message]: List of reasoning steps.
        """
        steps = self.reasoning_steps
        if filter_fn:
            steps = [step for step in steps if filter_fn(step)]

        if limit is not None:
            return steps[-limit:]
        return steps

    def calculate_technical_debt(self) -> float:
        """
        Calculate technical debt based on reasoning steps.

        Returns:
            float: Calculated technical debt.
        """
        if not self.reasoning_steps:
            return 0.0
        return sum(step.complexity_score or 0 for step in self.reasoning_steps) / len(
            self.reasoning_steps
        )

    def apply_bias_correction(
        self, correction: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Apply bias correction.

        Args:
            correction (str): Bias correction string.
            context (Optional[Dict[str, Any]], optional): Optional context for bias correction.
        """
        self.bias = correction
        # Optional: log or process context if needed

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Provide statistics about the agent's memory.

        Returns:
            Dict[str, Any]: A dictionary with memory-related statistics.
        """
        return {
            "total_steps": len(self.reasoning_steps),
            "bias_correction": self.bias is not None,
            "avg_complexity": self.calculate_technical_debt(),
        }


class AgentMemoryExtended(SimpleAgentMemory):
    def get_reasoning_history(self, filter_fn):
        # Updated parameter name
        pass  # Implement method

    def apply_bias_correction(self, correction, confidence, source):
        pass  # Implement method

    def some_method(self, arg1, arg2, arg3, arg4, arg5):
        pass  # Reduce number of arguments


class BaseLLMResponse(LLMResponse):
    """
    Base class for LLM responses.

    Provides a standard structure for LLM response information.
    """

    def __init__(
        self,
        text: str,
        tokens_used: int,
        finish_reason: Optional[str] = None,
        raw_response: Optional[Any] = None,
        complexity_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a base LLM response.

        Args:
            text (str): Generated text response.
            tokens_used (int): Number of tokens used.
            finish_reason (Optional[str], optional): Reason for response completion.
            raw_response (Optional[Any], optional): Raw response from the LLM.
            complexity_score (Optional[float], optional): Complexity score of the response.
            metadata (Optional[Dict[str, Any]], optional): Additional metadata about the response.
            generation_params (Optional[Dict[str, Any]], optional): Parameters used for generation.
        """
        self.text = text
        self.tokens_used = tokens_used
        self.finish_reason = finish_reason
        self.raw_response = raw_response
        self.complexity_score = complexity_score
        self.metadata = metadata or {}
        self.generation_params = generation_params or {}

    def get_response_summary(self) -> Dict[str, Any]:
        """
        Provide a summary of the response.

        Returns:
            Dict[str, Any]: A dictionary with response summary information.
        """
        return {
            "text_length": len(self.text),
            "tokens_used": self.tokens_used,
            "complexity_score": self.complexity_score,
            "finish_reason": self.finish_reason,
            **self.metadata,
        }

    def is_complete_response(self) -> bool:
        """
        Check if the response is considered complete.

        Returns:
            bool: True if the response is complete, False otherwise.
        """
        return self.finish_reason == "stop"


class BaseStreamingLLMResponse(StreamingLLMResponse):
    """
    Base class for streaming LLM responses.

    Provides an abstract base for implementing streaming response generators.
    """

    def __aiter__(self) -> AsyncGenerator[str, None]:
        """
        Async iterator for streaming response.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement __aiter__ method")

    async def collect_full_response(self) -> str:
        """
        Collect the full response from the streaming generator.

        Returns:
            str: The complete response text.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement collect_full_response method"
        )
