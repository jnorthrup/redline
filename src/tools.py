"""
Tools module.
"""


class Tool:
    """
    Represents a tool that can execute commands.
    """

    def __init__(self, name):
        self.name = name

    def execute(self, command):
        """
        Executes a tool-specific command.
        """
        # Implementation of command execution
        # ...existing code...

    def get_name(self):
        """
        Get the name of the tool.
        """
        return self.name
