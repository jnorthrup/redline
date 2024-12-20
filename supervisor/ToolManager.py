class ToolManager:
    def __init__(self):
        self.tools = [
            {
                "name": "exec",
                "description": "Executes shell commands.",
                "usage": "Use fence instructions to execute commands:\n```\nEXEC\n<command>\n```",
            },
            {
                "name": "websearch",
                "description": "Performs web searches.",
                "usage": "Use fence instructions to perform a web search:\n```\nWEBSERACH\n<query>\n```",
            },
        ]

    def execute_tool(self, tool_name: str, input_data: str) -> str:
        """Execute a tool with the given input data."""
        if not input_data:
            return "No input data provided"

        if tool_name == "exec":
            return self._execute_exec_tool(input_data)
        elif tool_name == "websearch":
            return self._execute_websearch_tool(input_data)
        else:
            return f"Unknown tool: {tool_name}"

    def _execute_exec_tool(self, command: str) -> str:
        """Execute a shell command."""
        # Implementation of command execution
        return f"Executed command: {command}"

    def _execute_websearch_tool(self, query: str) -> str:
        """Execute a web search."""
        # Implementation of web search
        return f"Searched for: {query}"
