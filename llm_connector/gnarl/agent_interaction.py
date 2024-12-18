"""
Module for agent interaction protocols and management.

This module defines abstract and concrete classes for managing agent interactions,
including methods for communication, reasoning, and state management in 
large language model (LLM) based agent systems.
"""

from typing import List, Optional, Dict, Any, Union

from .interfaces import (
    AgentMemory, LLMConnector, LLMResponse, 
    Message, ModelConfig, StreamingLLMResponse
)
from .charter import AbstractCharter
from .agent_interaction_helper import AgentInteractionHelper
from .reasoning_feedback_helper import ReasoningFeedbackHelper
from .metrics_helper import MetricsHelper  # Import MetricsHelper

class AbstractAgentInteraction(AbstractCharter):
    """
    Abstract base class for agent interaction protocols.

    Defines core methods for agent communication, reasoning, and interaction
    management across different types of agent systems.
    """

    def __init__(
        self, 
        connector: LLMConnector, 
        memory: AgentMemory, 
        config: Optional[ModelConfig] = None
    ):
        """
        Initialize the agent interaction system.

        Args:
            connector (LLMConnector): The LLM connector for generating responses.
            memory (AgentMemory): Memory system for tracking agent reasoning.
            config (Optional[ModelConfig], optional): Configuration for the interaction.
        """
        self.connector = connector
        self.memory = memory
        self.config = config or ModelConfig()
        self.interaction_history: List[Message] = []
        self.agent_interaction_helper = AgentInteractionHelper()
        self.reasoning_feedback_helper = ReasoningFeedbackHelper()
        self.metrics_helper = MetricsHelper()  # Initialize MetricsHelper

    @MetricsHelper.async_metrics_decorator
    async def generate_response(
        self, 
        messages: List[Message], 
        stream: bool = False
    ) -> Union[LLMResponse, StreamingLLMResponse]:
        """
        Generate a response using the configured LLM connector.

        Args:
            messages (List[Message]): Conversation history and current prompt.
            stream (bool, optional): Whether to use streaming response.

        Returns:
            Union[LLMResponse, StreamingLLMResponse]: Generated response.
        """
        return await self.agent_interaction_helper.generate_response(messages, stream)

    def store_interaction(self, message: Message) -> None:
        """
        Store an interaction message in the agent's memory.

        Args:
            message (Message): Message to store in interaction history.
        """
        self.reasoning_feedback_helper.process_message(message)
        self.interaction_history.append(message)
        self.memory.store_reasoning_step(message)

    def get_interaction_context(self, limit: Optional[int] = None) -> List[Message]:
        """
        Retrieve recent interaction context.

        Args:
            limit (Optional[int], optional): Number of recent interactions to retrieve.

        Returns:
            List[Message]: Recent interaction messages.
        """
        return self.interaction_history[-limit:] if limit else self.interaction_history

    def calculate_interaction_complexity(self) -> float:
        """
        Calculate the complexity of recent interactions.

        Returns:
            float: Calculated interaction complexity score.
        """
        return self.memory.calculate_technical_debt()

    def apply_interaction_bias_correction(self, correction: str) -> None:
        """
        Apply a bias correction to the agent's interaction model.

        Args:
            correction (str): Bias correction strategy or description.
        """
        self.memory.apply_bias_correction(correction)

    def get_interaction_stats(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive interaction statistics.

        Returns:
            Dict[str, Any]: Dictionary of interaction-related metrics.
        """
        return {
            "total_interactions": len(self.interaction_history),
            "memory_stats": self.memory.get_memory_stats(),
            "complexity_score": self.calculate_interaction_complexity()
        }

class ConversationalAgentInteraction(AbstractAgentInteraction):
    """
    Concrete implementation of an agent interaction system focused on conversational dynamics.
    """

    @MetricsHelper.async_metrics_decorator
    async def start_conversation(
        self, 
        initial_prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Initiate a new conversation through the agent pipeline.

        Args:
            initial_prompt (str): The starting message for the conversation.
            context (Optional[Dict[str, Any]], optional): Additional conversation context.

        Returns:
            LLMResponse: Response after processing through all stages.
        """
        initial_message = Message(
            role="user", 
            content=initial_prompt,
            context=context
        )
        self.store_interaction(initial_message)
        return await self.process_through_stages(initial_message)

    async def process_through_stages(self, message: Message) -> LLMResponse:
        """Process message through all charter-defined stages."""
        # Stage 2: Cognitive
        cognitive_result = await self.cognitive_agent.process(message)
        cognitive_handoff = self.memory.prepare_handoff(cognitive_result)
        
        # Stage 3: Planning
        self.memory.receive_handoff(cognitive_handoff)
        planning_result = await self.planning_agent.process(cognitive_result)
        planning_handoff = self.memory.prepare_handoff(planning_result)
        
        # Stage 4: Action
        self.memory.receive_handoff(planning_handoff)
        action_result = await self.action_agent.process(planning_result)
        action_handoff = self.memory.prepare_handoff(action_result)
        
        # Stage 5: Feedback
        self.memory.receive_handoff(action_handoff)
        return await self.feedback_agent.process(action_result)

    @MetricsHelper.async_metrics_decorator
    async def continue_conversation(
        self, 
        user_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Continue an existing conversation with a new user message.

        Args:
            user_message (str): The user's next message.
            context (Optional[Dict[str, Any]], optional): Additional message context.

        Returns:
            LLMResponse: Response from the LLM.
        """
        conversation_history = self.get_interaction_context()
        new_message = Message(
            role="user", 
            content=user_message
        )
        if context:
            new_message.context = context

        conversation_history.append(new_message)
        self.store_interaction(new_message)

        response = await self.generate_response(conversation_history)
        response_message = Message(
            role="assistant", 
            content=response.text, 
            complexity_score=response.complexity_score
        )
        self.store_interaction(response_message)

        return response

agent = Agent(model_type='type', model_name='name')  # Provided required arguments
