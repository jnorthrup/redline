"""
Interfaces for the GNARL (Generative Neural Adaptive Reasoning Layer) system.

Defines core protocols, data structures, and type definitions for 
agent-based reasoning and interaction with Large Language Models.
"""

from __future__ import annotations

import abc
import dataclasses
import enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Protocol

class ModelType(enum.Enum):
    """
    Enumeration of supported Large Language Model types.

    Provides a standardized way to specify different LLM providers
    and model architectures, making it easier to extend support
    for new models in the future.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    CUSTOM = "custom"


@dataclasses.dataclass
class ModelConfig:
    """
    Configuration parameters for initializing an LLM connection.

    Provides a flexible and type-safe way to configure LLM connections
    with sensible defaults and clear documentation.
    """

    model_type: ModelType
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the configuration.

        Returns:
            Dict[str, Any]: A dictionary containing key configuration details.
        """
        return {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "timeout": self.timeout,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for the configuration.

        Args:
            api_key (str): The API key to be set.
        """
        self.api_key = api_key

    def set_base_url(self, base_url: str) -> None:
        """
        Set the base URL for the configuration.

        Args:
            base_url (str): The base URL to be set.
        """
        self.base_url = base_url


class MessageRole(enum.Enum):
    """
    Standardized message roles for conversational LLM interactions.

    Provides a consistent way to specify message origins and types
    across different LLM providers.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    REASONING = "reasoning"
    BIAS_CORRECTION = "bias_correction"


@dataclasses.dataclass
class Message:
    """
    Represents a single message in an LLM conversation.
    """

    role: MessageRole
    content: str
    name: Optional[str] = None
    complexity_score: Optional[float] = None
    bias_correction: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the message.

        Returns:
            Dict[str, Any]: A dictionary containing key message details.
        """
        return {
            "role": self.role,
            "content": self.content[:50],  # First 50 characters
            "complexity_score": self.complexity_score,
        }


class AgentMemory(Protocol):
    """
    Protocol defining the interface for agent memory management.

    Enables tracking of reasoning history, technical debt,
    and bias correction.
    """

    bias: Optional[str]
    reasoning_complexity: float
    memory_capacity: int

    def store_reasoning_step(self, message: Message) -> None:
        """
        Store a reasoning step in the agent's memory.

        Args:
            message (Message): The reasoning step to store.
        """
        raise NotImplementedError("Subclasses must implement store_reasoning_step")

    def get_reasoning_history(
        self, limit: Optional[int] = None, filter_role: Optional[MessageRole] = None
    ) -> List[Message]:
        """
        Retrieve recent reasoning history.

        Args:
            limit (Optional[int], optional): Maximum number of steps to retrieve.
            filter_role (Optional[MessageRole], optional): Filter steps by role.

        Returns:
            List[Message]: List of reasoning steps.
        """
        raise NotImplementedError("Subclasses must implement get_reasoning_history")

    def calculate_technical_debt(self) -> float:
        """
        Calculate the current technical debt.

        Returns:
            float: Calculated technical debt score.
        """
        raise NotImplementedError("Subclasses must implement calculate_technical_debt")

    def apply_bias_correction(
        self, correction: str, confidence: float = 0.5, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply a bias correction to the agent's memory.

        Args:
            correction (str): The bias correction to apply.
            confidence (float, optional): Confidence level of the correction. Defaults to 0.5.
            source (Optional[str], optional): Source of the bias correction.

        Returns:
            Dict[str, Any]: Details of the bias correction application.
        """
        raise NotImplementedError("Subclasses must implement apply_bias_correction")

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive memory statistics.

        Returns:
            Dict[str, Any]: Dictionary of memory-related metrics.
        """
        raise NotImplementedError("Subclasses must implement get_memory_stats")


class LLMResponse(Protocol):
    """
    Protocol defining the standard interface for LLM responses.

    Ensures that different LLM implementations provide a
    consistent response structure.
    """

    text: str
    tokens_used: int
    finish_reason: Optional[str]
    raw_response: Any
    complexity_score: Optional[float]

    def get_response_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the response.

        Returns:
            Dict[str, Any]: A dictionary containing key response details.
        """
        return {
            "text": self.text[:50],  # First 50 characters
            "tokens_used": self.tokens_used,
            "finish_reason": self.finish_reason,
        }

    def get_tokens_used(self) -> int:
        """
        Get the number of tokens used in the response.

        Returns:
            int: Number of tokens used.
        """
        return self.tokens_used

    def get_finish_reason(self) -> Optional[str]:
        """
        Get the reason for response completion.

        Returns:
            Optional[str]: Reason for response completion.
        """
        return self.finish_reason


class StreamingLLMResponse(Protocol):
    """
    Protocol for streaming LLM responses, supporting
    incremental generation.
    """

    def __aiter__(self) -> AsyncGenerator[str, None]:
        """
        Async iterator for streaming response tokens.

        Yields:
            str: Incrementally generated response tokens.
        """
        raise NotImplementedError("Subclasses must implement __aiter__")

    def get_raw_response(self) -> Any:
        """
        Retrieve the raw response object.

        Returns:
            Any: Raw response from the LLM.
        """
        raise NotImplementedError("Subclasses must implement get_raw_response")


class LLMConnector(Protocol):
    """
    Core protocol for interacting with Large Language Models.

    Defines the essential methods for LLM communication,
    providing a flexible and extensible interface for
    agent-based reasoning.
    """

    @abc.abstractmethod
    async def generate(
        self,
        messages: List[Message],
        config: Optional[ModelConfig] = None,
        agent_memory: Optional[AgentMemory] = None,
    ) -> LLMResponse:
        """
        Generate a complete response from the LLM with
        enhanced reasoning tracking.

        Args:
            messages (List[Message]): Conversation history and current prompt.
            config (Optional[ModelConfig], optional): Configuration for the generation.
            agent_memory (Optional[AgentMemory], optional): Memory tracking for reasoning.

        Returns:
            LLMResponse: Generated response from the LLM.
        """
        raise NotImplementedError("Subclasses must implement generate method")

    @abc.abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        config: Optional[ModelConfig] = None,
        agent_memory: Optional[AgentMemory] = None,
    ) -> StreamingLLMResponse:
        """
        Generate a streaming response from the LLM with
        enhanced reasoning tracking.

        Args:
            messages (List[Message]): Conversation history and current prompt.
            config (Optional[ModelConfig], optional): Configuration for the generation.
            agent_memory (Optional[AgentMemory], optional): Memory tracking for reasoning.

        Returns:
            StreamingLLMResponse: Streaming response from the LLM.
        """
        raise NotImplementedError("Subclasses must implement generate_stream method")

    @abc.abstractmethod
    async def validate_config(self, config: ModelConfig) -> bool:
        """
        Validate the provided model configuration.

        Args:
            config (ModelConfig): Configuration to validate.

        Returns:
            bool: Whether the configuration is valid.
        """
        raise NotImplementedError("Subclasses must implement validate_config method")


class LLMError(Exception):
    """
    Base exception for LLM-related errors.

    Provides a standardized error handling mechanism for
    LLM connection and generation issues.
    """


class LLMConnectionError(LLMError):
    """
    Raised when there are issues establishing an LLM connection.
    """


class TokenLimitExceededError(LLMError):
    """
    Raised when input or output tokens exceed model limitations.
    """


def create_system_message(
    content: str, complexity_score: Optional[float] = None
) -> Message:
    """
    Convenience method to create a system message.

    Args:
        content (str): Content of the system message.
        complexity_score (Optional[float], optional): Complexity score of the message.

    Returns:
        Message: A system message instance.
    """
    return Message(
        role=MessageRole.SYSTEM, content=content, complexity_score=complexity_score
    )


def create_user_message(
    content: str, complexity_score: Optional[float] = None
) -> Message:
    """
    Convenience method to create a user message.

    Args:
        content (str): Content of the user message.
        complexity_score (Optional[float], optional): Complexity score of the message.

    Returns:
        Message: A user message instance.
    """
    return Message(
        role=MessageRole.USER, content=content, complexity_score=complexity_score
    )


def create_reasoning_message(
    content: str, complexity_score: Optional[float] = None
) -> Message:
    """
    Convenience method to create an explicit reasoning message.

    Args:
        content (str): Content of the reasoning message.
        complexity_score (Optional[float], optional): Complexity score of the message.

    Returns:
        Message: A reasoning message instance.
    """
    return Message(
        role=MessageRole.REASONING, content=content, complexity_score=complexity_score
    )


class SomeClass:
    # Reduced instance attributes
    attribute1: Type
    attribute2: Type
