"""
Test module for LLM Connector interfaces.

This module provides type checking and basic interface validation
to ensure the core protocols are correctly defined.
"""

import typing

import pytest

from llm_connector.gnarl.interfaces import (
    LLMConnector,
    LLMResponse,
    Message,
    MessageRole,
    ModelConfig,
    ModelType,
    StreamingLLMResponse,
)


def test_model_config_creation():
    """
    Validate that ModelConfig can be created with various parameters.
    """
    config = ModelConfig(
        model_type=ModelType.OPENAI,
        model_name="gpt-4",
        temperature=0.7,
        max_tokens=1000,
    )

    assert config.model_type == ModelType.OPENAI
    assert config.model_name == "gpt-4"
    assert config.temperature == 0.7
    assert config.max_tokens == 1000


def test_message_creation():
    """
    Ensure Message objects can be created with different roles.
    """
    system_msg = Message(role=MessageRole.SYSTEM, content="You are a helpful assistant")
    user_msg = Message(role=MessageRole.USER, content="Explain quantum computing")

    assert system_msg.role == MessageRole.SYSTEM
    assert user_msg.role == MessageRole.USER


def test_llm_connector_protocol():
    """
    Verify that LLMConnector protocol requires specific methods.
    """

    # This is a type-checking test to ensure the protocol is correctly defined
    def validate_connector(connector: LLMConnector):
        assert hasattr(connector, "generate")
        assert hasattr(connector, "generate_stream")
        assert hasattr(connector, "validate_config")

        # Ensure methods are async
        assert typing.is_async_callable(connector.generate)
        assert typing.is_async_callable(connector.generate_stream)
        assert typing.is_async_callable(connector.validate_config)


def test_response_protocols():
    """
    Validate the structure of LLM response protocols.
    """

    def check_llm_response(response: LLMResponse):
        assert hasattr(response, "text")
        assert hasattr(response, "tokens_used")
        assert hasattr(response, "finish_reason")
        assert hasattr(response, "raw_response")

    def check_streaming_response(response: StreamingLLMResponse):
        # Ensure the response is an async iterator
        assert hasattr(response, "__aiter__")


# Example mock implementation for demonstration
class MockLLMConnector:
    """
    A mock implementation to demonstrate the LLMConnector protocol.

    This is NOT a functional implementation, just a type-checking example.
    """

    async def generate(
        self,
        messages: typing.List[Message],
        config: typing.Optional[ModelConfig] = None,
    ) -> LLMResponse:
        # Simulated implementation
        class MockResponse:
            text = "Mock response"
            tokens_used = 10
            finish_reason = "stop"
            raw_response = {}

        return MockResponse()

    async def generate_stream(
        self,
        messages: typing.List[Message],
        config: typing.Optional[ModelConfig] = None,
    ) -> StreamingLLMResponse:
        # Simulated async generator
        async def mock_stream():
            yield "Mock"
            yield " streaming"
            yield " response"

        return mock_stream()

    async def validate_config(self, config: ModelConfig) -> bool:
        return True


@pytest.mark.asyncio
async def test_mock_connector():
    """
    Demonstrate a basic usage of a mock LLM connector.
    """
    connector = MockLLMConnector()

    # Test generate method
    messages = [Message(role=MessageRole.USER, content="Hello")]
    response = await connector.generate(messages)
    assert response.text == "Mock response"

    # Test streaming method
    stream_response = await connector.generate_stream(messages)
    collected = []
    async for token in stream_response:
        collected.append(token)

    assert "".join(collected) == "Mock streaming response"
