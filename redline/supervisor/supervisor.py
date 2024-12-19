"""
Module for supervisor operations.
"""

import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.providers.generic import GenericProvider
from redline.supervisor.providers import LLMProvider
from redline.supervisor.WebSearch import WebSearch
from redline.supervisor.QwenProvider import QwenProvider
from redline.controllers.status_line_controller import StatusLineController
from redline.models.status_line_config import StatusLineConfig
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.ProviderManager import ProviderManager
from redline.supervisor.SystemPromptHandler import SystemPromptHandler
from redline.supervisor.utils import DebouncedLogger, setup_logging, format_bytes
from redline.supervisor.cognitive.explanation_generator import ExplanationGenerator
from redline.supervisor.cognitive.gap_identifier import GapIdentifier
from redline.supervisor.cognitive.finding_derivation import FindingDerivation

setup_logging()

@dataclass
class SupervisorConfig:
    """Configuration for Supervisor"""
    model_name: str = "granite-3.1-2b-instruct"  # Update to match LM Studio model
    api_base: str = "http://localhost:1234/v1"    # Update to LM Studio URL
    max_retries: int = 3
    timeout: int = 30

class Supervisor:
    def __init__(self, config: SupervisorConfig = SupervisorConfig()):
        self.config = config
        self.message_handler = MessageHandler()
        self.system_prompt_handler = SystemPromptHandler(self.message_handler)
        self.provider_manager = ProviderManager()
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        
        # Initialize cognitive agent components
        self.explanation_generator = ExplanationGenerator(self.memory_manager)
        self.gap_identifier = GapIdentifier(self.memory_manager)
        self.finding_derivation = FindingDerivation(self.memory_manager)
        
        # Initialize status line
        status_config = StatusLineConfig()
        self.status_line = StatusLineController(status_config)
        
        # Initialize logger
        self.logger = DebouncedLogger(interval=5.0)
        
        # Initialize web search
        self.web_search_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.web_search_api_key:
            self.logger.warning("PERPLEXITY_API_KEY not set")
        self.web_search = WebSearch(self.web_search_api_key)
        
        # Initialize metrics
        self.active_model = "None"
        self.sent_bytes = 0
        self.received_bytes = 0
        
        # Update initial system prompt
        self.system_prompt_handler.update_system_prompt(self)

        # Run startup commands
        self.run_startup_commands()

    def evaluate_agent_competence(self, conversation_history: str) -> Dict[str, Any]:
        """Evaluate another agent's competence using the ladder framework.
        
        Args:
            conversation_history: The conversation to analyze
            
        Returns:
            Dict containing competence evaluation metrics
        """
        evaluation_prompt = """Analyze the following conversation and evaluate the agent's competence:

        1. Rate the agent's base competence (1-10):
        - How well does it handle basic queries?
        - Does it provide coherent responses?
        - Can it engage in basic reasoning?

        2. Identify any exceptional capabilities:
        - Areas where the agent exceeded expectations
        - Demonstrated deep domain knowledge
        - Novel or creative problem-solving

        3. Note any competence gaps:
        - Topics where the agent struggled
        - Missed context or implications
        - Incomplete or incorrect responses

        4. Recommend escalation level:
        - Should this conversation be escalated to a more capable model?
        - What capabilities would a higher-tier model provide?
        - What specific improvements are needed?

        Conversation to analyze:
        {conversation}
        """
        
        # Get evaluation from current provider
        response = self.current_provider.generate(
            evaluation_prompt.format(conversation=conversation_history),
            self.get_system_prompt()
        )
        
        # Parse and structure the evaluation
        try:
            evaluation = {
                "base_competence_score": self._extract_score(response),
                "exceptional_capabilities": self._extract_section(response, "exceptional capabilities"),
                "competence_gaps": self._extract_section(response, "competence gaps"),
                "recommended_escalation": self._extract_section(response, "recommend escalation"),
                "raw_evaluation": response
            }
            return evaluation
        except Exception as e:
            self.logger.error(f"Error parsing evaluation: {e}")
            return {"error": str(e), "raw_evaluation": response}

    def _extract_score(self, response: str) -> int:
        """Extract numerical competence score from response."""
        try:
            scores = re.findall(r'(?:rate|score|competence).*?(\d+)(?:/10)?', 
                              response.lower())
            if scores:
                score = int(scores[0])
                return min(max(score, 1), 10)  # Ensure score is 1-10
            return 5  # Default middle score if none found
        except Exception:
            return 5

    def _extract_section(self, response: str, section_name: str) -> List[str]:
        """Extract a specific section from the evaluation response."""
        try:
            pattern = f"{section_name}.*?:(.*?)(?:\n\d|$)"
            matches = re.findall(pattern, response.lower(), re.DOTALL)
            if matches:
                points = [p.strip('- \n') for p in matches[0].split('\n') 
                         if p.strip('- \n')]
                return points
            return []
        except Exception:
            return []

    def set_active_provider(self, provider: LLMProvider, model_name: str):
        """Set the active provider and model name."""
        self.current_provider = provider
        self.active_model = model_name
        self.system_prompt_handler.update_system_prompt(self)
        
    def set_standby_provider(self, provider: LLMProvider):
        """Set the standby provider."""
        self.standby_provider = provider

    def run_startup_commands(self):
        """Run any necessary startup commands."""
        pass

    def get_system_prompt(self) -> str:
        """Get the current system prompt."""
        return self.message_handler.get_system_prompt()
