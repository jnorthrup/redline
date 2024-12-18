import asyncio
from typing import Dict, Any, List
from gnarl.agents.base import BaseAgent
from gnarl.agents.cognitive_agent import CognitiveAgent
from gnarl.agents.planning_agent import PlanningAgent
from gnarl.connector import SimpleAgentMemory
from gnarl.metrics_helper import MetricsHelper

class BeneficiaryAgent(BaseAgent):
    def __init__(self):
        self.memory = SimpleAgentMemory()
        self.metrics = MetricsHelper()
        self.agents: List[BaseAgent] = [
            CognitiveAgent(),
            PlanningAgent()
        ]
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        current_data = input_data
        
        for agent in self.agents:
            # Process through each agent in pipeline
            result = await agent.process(current_data)
            
            # Update memory and prepare handoff
            self.memory.update(result)
            current_data = self.memory.prepare_handoff(result)
            
        return current_data

async def interactive_console():
    beneficiary = BeneficiaryAgent()
    
    print("GNARL Interactive Console")
    print("------------------------")
    print("Enter your queries (type 'exit' to quit)")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                break
                
            # Process through agent pipeline
            result = await beneficiary.process({"user_input": user_input})
            
            # Prepare for next stage handoff
            handoff = beneficiary.memory.prepare_handoff(result)
            print(f"\nSystem: Processing complete. Stage: {result['stage']}")
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(interactive_console())
