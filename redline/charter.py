"""
Module defining abstract base classes for LLM charter components.

This module provides abstract base classes that define the core interfaces
and methods for various components in the LLM (Large Language Model) charter
system, including models, connectors, and tournaments.
"""

from abc import ABC
from typing import Any, Dict, List, Optional

from .interfaces import AgentMemory  # Ensure correct import path
from .interfaces import LLMResponse, Message, ModelConfig
from .tournament_evaluation_helper import TournamentEvaluationHelper


class AbstractCharter(ABC):
    """
    Abstract base class for the charter hierarchy.

    Provides a common interface for charter-related components.
    """

    def initialize(self):
        """
        Default initialization method.

        Subclasses can override this method to provide specific initialization logic.
        """
        return None

    def get_charter_type(self) -> str:
        """
        Provide a default method to get the charter type.

        Returns:
            str: The type of charter, defaults to class name.
        """
        return self.__class__.__name__

    def assess_gaps(self) -> Dict[str, Any]:
        """
        Assess gaps in the charter and suggest measures to take.

        Returns:
            Dict containing gap assessment and suggested measures.
        """
        # Placeholder for gap assessment logic
        gaps = ["Lack of detailed implementation", "Need for more robust testing"]
        measures = ["Develop detailed implementation plans", "Increase test coverage"]

        return {
            "gaps": gaps,
            "measures": measures,
        }

    def assess_code_alignment(self) -> Dict[str, Any]:
        """
        Assess the code and ensure it aligns with the vision of the charter.

        Returns:
            Dict containing alignment assessment and suggested improvements.
        """
        # Placeholder for code alignment logic
        alignment_issues = ["Inconsistent naming conventions", "Lack of comments"]
        improvements = ["Standardize naming conventions", "Add comments for clarity"]

        return {
            "alignment_issues": alignment_issues,
            "improvements": improvements,
        }


class AbstractModel(AbstractCharter):
    """
    Abstract base class for models.

    Defines the core interface for generating responses in the charter system.
    """

    def generate_response(
        self, messages: List[Message], config: ModelConfig, agent_memory: AgentMemory
    ) -> LLMResponse:
        """
        Generate a response from the model.

        Args:
            messages (List[Message]): Conversation history and current prompt
            config (ModelConfig): Configuration for the model
            agent_memory (AgentMemory): Agent memory for tracking reasoning

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_response method")

    def get_model_capabilities(self) -> dict:
        """
        Provide a default method to get model capabilities.

        Returns:
            dict: A dictionary of model capabilities.
        """
        return {"name": self.__class__.__name__}


class AbstractConnector(AbstractCharter):
    """
    Abstract base class for connectors.

    Defines methods for connecting and disconnecting from LLM providers.
    """

    def connect(self, config: ModelConfig):
        """
        Connect to the LLM provider.

        Args:
            config (ModelConfig): Configuration for the connector

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement connect method")

    def disconnect(self):
        """
        Disconnect from the LLM provider.

        This method must be implemented to provide proper cleanup
        and resource management when disconnecting.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement disconnect method")

    def get_connection_status(self) -> bool:
        """
        Provide a default method to check connection status.

        Returns:
            bool: Connection status, defaults to False.
        """
        return False


class AbstractTournament(AbstractCharter):
    """
    Abstract base class for tournaments.

    Defines the interface for running tournaments between different
    LLM connectors to compare their performance.
    """

    def __init__(self):
        self.tournament_helper = TournamentEvaluationHelper()

    def run_tournament(
        self,
        connectors: List[AbstractConnector],
        messages: List[Message],
        config: ModelConfig,
        agent_memory: Optional[AgentMemory] = None,
    ) -> List[LLMResponse]:
        """
        Run a tournament with the given connectors.

        Args:
            connectors (List[AbstractConnector]): List of connectors to participate
                in the tournament
            messages (List[Message]): Conversation history and current prompt
            config (ModelConfig): Configuration for the tournament
            agent_memory (Optional[AgentMemory]): Agent memory for tracking reasoning

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        return self.tournament_helper.run_tournament(
            connectors, messages, config, agent_memory
        )

    def get_tournament_results(self) -> dict:
        """
        Provide a default method to get tournament results.

        Returns:
            dict: A dictionary of tournament results.
        """
        return self.tournament_helper.get_results()
