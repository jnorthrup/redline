import asyncio
from typing import Any, Dict

from redline.agents.base import BaseAgent
# from redline.agents.cognitive_agent import CognitiveAgent
from redline.agents.planning_agent import PlanningAgent


class BeneficiaryAgent:
    def __init__(self, memory, toolkit):
        self.memory = memory
        self.toolkit = toolkit
        # self.cognitive_agent = CognitiveAgent(memory, toolkit)
        self.planning_agent = PlanningAgent(memory, toolkit)

    async def process_input(self, user_input: str) -> Dict[str, Any]:
        input_data = {"user_input": user_input}
        # cognitive_result = await self.cognitive_agent.process(input_data)
        planning_result = await self.planning_agent.process(input_data)
        return {
            # "cognitive_result": cognitive_result,
            "planning_result": planning_result,
        }


async def interactive_console():
    # Example memory and toolkit (these should be replaced with actual implementations)
    memory = {}
    toolkit = {}

    beneficiary = BeneficiaryAgent(memory, toolkit)
    while True:
        try:
            user_input = input("Enter your input: ")
            if user_input.lower() == "exit":
                break
            result = await beneficiary.process_input(user_input)
            print(result)
        except EOFError:
            print("Exiting interactive console.")
            break


if __name__ == "__main__":
    asyncio.run(interactive_console())
