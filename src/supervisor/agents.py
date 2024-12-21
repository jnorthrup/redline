from typing import Any, Dict, List


class Agent:
    def __init__(self, name: str, memory: Dict[str, Any], tools: List[Any]):
        self.name = name
        self.memory = memory
        self.tools = tools
        self.uplink = None  # Initialize uplink

    def set_uplink(self, uplink: Any):
        self.uplink = uplink

    def perform_action(self, action: str):
        # Implementation of action
        pass


class FeedbackLoopAgent(Agent):
    def evaluate_observations(self, observations: str):
        # Evaluate and update plan
        pass


class CompletionAgent(Agent):
    def verify_completion(self):
        # Verify task completion
        pass


class SupervisorAgent(Agent):
    def revise_handoff(self, agent: Agent):
        # Revise bias based on agent's request
        pass
