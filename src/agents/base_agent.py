class Agent:
    def __init__(self, name, memory, tools):
        self.name = name
        self.memory = memory
        self.tools = tools

    def perform_action(self, action):
        # Execute the action using the available tools
        output = action.execute(self.tools)
        # Collect observations and update memory
        self.memory.update_memory(output)
        return output