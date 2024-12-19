from typing import Dict, Type

from .base import Agent
from .cognitive import CognitiveAgent
from .execution import ExecutionAgent
from .feedback import FeedbackAgent
from .planning import PlanningAgent


class AgentFramework:
    """Framework for managing agent interactions"""

    def __init__(self):
        # Initialize agents
        self.cognitive = CognitiveAgent()
        self.planning = PlanningAgent()
        self.execution = ExecutionAgent()
        self.feedback = FeedbackAgent()

        # Connect agent pipeline
        self.cognitive._downstream_agent = self.planning
        self.planning._upstream_agent = self.cognitive
        self.planning._downstream_agent = self.execution
        self.execution._upstream_agent = self.planning
        self.execution._downstream_agent = self.feedback
        self.feedback._upstream_agent = self.execution

        # Initialize reward system
        self.rewards = {
            "technical_debt_reduction": lambda x: x / (x**3),  # Tokens needed cubed
        }

    def process_task(self, task: Dict) -> None:
        """Begin processing with cognitive agent"""
        self.cognitive.process(task)

    def get_agent_memory(self, agent_type: Type[Agent]) -> Dict:
        """Retrieve agent memory for analysis"""
        agent = self._get_agent_instance(agent_type)
        return agent._memory.data if agent else None

    def _get_agent_instance(self, agent_type: Type[Agent]) -> Agent:
        """Get agent instance by type"""
        for agent in [self.cognitive, self.planning, self.execution, self.feedback]:
            if isinstance(agent, agent_type):
                return agent
        return None
