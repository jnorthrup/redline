class Tool:
    def __init__(self, name):
        self.name = name

    def execute(self, command):
        print(f"Executing {self.name} tool with command: {command}")
        # Execute tool-specific command
        pass
