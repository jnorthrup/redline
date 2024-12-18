"""Supervisor agent for managing the GNARL agent pipeline."""

import time
from typing import Any, Dict, List

from ..metrics.instruments import MACD, RSI, MetricReading, Volatility
from .base import BaseAgent
from .core import ActionAgent, CognitiveAgent, FeedbackAgent, PlanningAgent


class SupervisorAgent:
    """Manages the agent pipeline and handles bias corrections"""

    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.instruments = {"rsi": RSI(), "macd": MACD(), "volatility": Volatility()}

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        current_data = task

        for agent in self.agents:
            # Process through agent
            result = await agent.process(current_data)

            # Update instruments
            for instrument in self.instruments.values():
                instrument.add_reading(
                    MetricReading(
                        value=agent.memory.calculate_technical_debt(),
                        timestamp=time.time(),
                        confidence=1.0,
                    )
                )

            # Prepare handoff
            current_data = {
                "previous_stage": result,
                "instruments": {
                    name: inst.calculate() for name, inst in self.instruments.items()
                },
            }

        return current_data
