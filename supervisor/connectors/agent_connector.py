from typing import Any, Dict
import logging

from supervisor.agents.agent_base import Agent
from supervisor.agents.reasoning_agent import ReasoningAgent
from supervisor.agents.planning_agent import PlanningAgent
from supervisor.agents.action_agent import ActionAgent
from supervisor.agents.feedback_agent import FeedbackAgent
from supervisor.agents.completion_agent import CompletionAgent

from supervisor.memory.manager import MemoryManager
from supervisor.providers import LLMProvider
from supervisor.providers.generic import GenericProvider
from supervisor.config import SupervisorConfig


class AgentConnector:
    """
    The AgentConnector is responsible for:
    1) Instantiating each agent with its private memory and tools.
    2) Sequencing how data flows from one agent to the next.
    3) Allowing an agent to request "corrective bias" from the Supervisor
       or any upstream aggregator, if the agent’s memory/analysis is incomplete.
    4) Calculating or retrieving the reward context (technical debt offset
       vs. tokens-used^3) to help each agent shape its plan.
    """

    def __init__(self, supervisor_config: SupervisorConfig):
        self.logger = logging.getLogger(__name__)

        # Shared or global context
        self.supervisor_config = supervisor_config

        # Example single shared memory manager, or one per agent
        self.root_memory = MemoryManager()

        # Agents: Each agent is given only the references it needs.
        self.reasoning_agent = ReasoningAgent()
        self.planning_agent = PlanningAgent()
        self.action_agent = ActionAgent()
        self.feedback_agent = FeedbackAgent()
        self.completion_agent = CompletionAgent()

        # Example: A default LLM provider with “generic” or “qwen”
        provider_config = {
            "api_base": "http://localhost:1234/v1",
            "model": "generic-model"
        }
        self.default_provider: LLMProvider = GenericProvider(config=provider_config)

        # Example: partial reward context
        self.reward_context = {
            "technical_debt_offset": 0.0,  # from config or updated in real usage
            "tokens_needed": 1            # from config or updated in real usage
        }

    def run_all_agents(self, data: Any) -> Any:
        """
        High-level example of passing data through all agents:
          1) Reasoning
          2) Planning
          3) Action
          4) Feedback
          5) (Optionally) ask upstream for bias correction
          6) Completion
        """
        self.logger.info("Starting agent data flow pipeline...")

        # Agent #1: Reasoning
        reasoning_result = self.reasoning_agent.process(data)

        # Agent #2: Planning
        plan = self.planning_agent.plan(reasoning_result)

        # Agent #3: Action
        action_result = self.action_agent.execute(plan)

        # Agent #4: Feedback
        feedback = self.feedback_agent.provide_feedback(action_result)

        # Optionally, an agent might request bias correction from the supervisor
        # if it deems that some upstream weighting is needed:
        if self.agent_requests_bias_correction(feedback):
            self.request_bias_correction("supervisor", reason="Refine plan or approach")

        # Agent #5: Completion
        final_output = self.completion_agent.finalize(action_result)

        # Optionally, update local or global memory with final output
        self.root_memory.store("last_run_output", {"result": final_output})
        self.logger.info("Agent pipeline complete. Final output ready.")

        return final_output

    def request_bias_correction(self, upstream: str, reason: str):
        """
        Example method for requesting an upstream “supervisor agent” or
        aggregator to correct or refine biases, e.g., changing how the
        reward function is calculated or adjusting the LLM’s model.
        """
        self.logger.info(
            f"Requesting upstream bias correction from {upstream} due to: {reason}"
        )
        # This method could directly call a method on the Supervisor
        # or simply set a flag in memory for the Supervisor to read.

    def agent_requests_bias_correction(self, feedback: Any) -> bool:
        """
        Example heuristic to decide if an agent’s feedback indicates we need
        to escalate for bias correction.
        """
        # Simple placeholder logic: if feedback is `None` or empty, request bias correction:
        return not feedback

    def compute_reward(self) -> float:
        """
        Example: Reward function = (technical_debt_offset) / (tokens_needed^3)
        """
        tdo = self.reward_context["technical_debt_offset"]
        tokens = self.reward_context["tokens_needed"]
        return self.supervisor_config.calculate_reward(tdo, tokens)
