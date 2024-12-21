from agent_base import Agent

class CompletionAgent(Agent):
    def __init__(self, name, memory, tools):
        super().__init__(name, memory, tools)

    def verify_completion(self):
        technical_debt = self.memory.calculate_technical_debt()
        tokens_needed = self.memory.calculate_tokens_needed()
        reward = self.memory.reward_system.calculate_reward(technical_debt, tokens_needed)
        threshold = 10  # Example threshold
        if reward < threshold:
            return False
        self.issue_completion_status()
        return True

    def issue_completion_status(self):
        # Issue completion status as per CHARTER.md
        status = "FINISH"
        if self.downstream:
            self.downstream.receive(status)
