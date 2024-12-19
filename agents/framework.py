from typing import Dict, Type
import logging

from .base import Agent
from .cognitive import CognitiveAgent
from .execution import ExecutionAgent
from .feedback import FeedbackAgent
from .planning import PlanningAgent
from .memory import MemoryManager
from .tools import ToolRegistry
from .metrics import MetricsTracker


class AgentFramework:
    """Framework for managing agent interactions"""

    def __init__(self):
        # Initialize managers
        self.memory = MemoryManager()
        self.tools = ToolRegistry()
        self.metrics = MetricsTracker()
        
        # Initialize agents
        self.cognitive = CognitiveAgent()
        self.planning = PlanningAgent()
        self.execution = ExecutionAgent() 
        self.feedback = FeedbackAgent()
        
        # Assign agent IDs
        for name, agent in [
            ("cognitive", self.cognitive),
            ("planning", self.planning),
            ("execution", self.execution),
            ("feedback", self.feedback)
        ]:
            agent.id = name
            agent._memory = self.memory.get_store(name)

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
