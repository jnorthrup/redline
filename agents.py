class Agent:
    def __init__(self, name, memory, tools, reward_system, upstream=None, downstream=None):
        self.name = name
        self.memory = memory
        self.tools = tools
        self.reward_system = reward_system
        self.upstream = upstream
        self.downstream = downstream
        self.bias = 1.0

    def set_handoff(self, upstream, downstream):
        self.upstream = upstream
        self.downstream = downstream

    def perform_action(self, action):
        result = self.tools.execute(action)
        self.memory.update_memory(action, result)
        if self.downstream:
            self.downstream.receive(result)
        return result

    def receive(self, data):
        self.memory.update_memory(data, None)
        if self.upstream:
            self.upstream.update_bias(data.get('correction', 0))

    def update_bias(self, correction):
        self.bias += correction

class FeedbackLoopAgent(Agent):
    def evaluate_observations(self):
        latest_obs, _ = self.memory.get_latest()
        # Evaluate and update plan based on latest observations
        # Placeholder implementation
        return f"Evaluated: {latest_obs}"

class CompletionAgent(Agent):
    def verify_completion(self):
        # Verify if tasks are completed
        # Placeholder implementation
        return "FINISH"

class SupervisorAgent(Agent):
    def revise_handoff(self, agent, correction):
        # Revise bias based on agent's request
        agent.update_bias(correction)
