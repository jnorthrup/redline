from agent_base import Agent


class PlanningAgent(Agent):
    def __init__(self, name, memory, tools):
        super().__init__(name, memory, tools)
        self.plan = []
