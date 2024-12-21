class ActionAgent(Agent):
    def __init__(self, name, memory, tools):
        super().__init__(name, memory, tools)

    def execute_action(self, action):
        # Execute the given action using the available tools
        output = self.perform_action(action)
        # Collect observations from the action
        observations = self.memory.update_memory(output)
        return observations

    def perform_action(self, action):
        # Placeholder for action execution logic
        # This should interact with the tools and return the output
        return f"Action '{action}' executed."