import asyncio
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
from .message_bus import MessageBus


class AgentFramework:
    """Framework for managing agent interactions"""

    def __init__(self):
        # Add message bus
        self.message_bus = MessageBus()
        
        # Initialize managers
        self.memory = MemoryManager()
        self.tools = ToolRegistry()
        self.metrics = MetricsTracker()
        
        # Initialize agents
        self.cognitive = CognitiveAgent()
        self.planning = PlanningAgent()
        self.execution = ExecutionAgent() 
        self.feedback = FeedbackAgent()
        
        # Set up message bus subscriptions
        self._setup_message_subscriptions()

        # Initialize reward system
        self.rewards = {
            "technical_debt_reduction": lambda x: x / (x**3),  # Tokens needed cubed
        }

    def _setup_message_subscriptions(self):
        """Set up message bus subscriptions for all agents"""
        agents = {
            "cognitive": self.cognitive,
            "planning": self.planning,
            "execution": self.execution,
            "feedback": self.feedback
        }

        for name, agent in agents.items():
            agent.id = name
            agent._memory = self.memory.get_store(name)
            # Subscribe agent to its topic
            self.message_bus.subscribe(
                f"agent.{name}",
                agent._message_queue
            )

    async def process_task(self, task: Dict) -> None:
        """Begin processing with cognitive agent"""
        await self.message_bus.publish("agent.cognitive", {
            "type": "task",
            "content": task
        })

    async def run(self):
        """Run all agents"""
        agent_tasks = [
            self.cognitive.run(),
            self.planning.run(),
            self.execution.run(),
            self.feedback.run()
        ]
        await asyncio.gather(*agent_tasks)

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
