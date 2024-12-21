"""
Module for managing tools.
"""

from typing import Any, Dict, List, Optional
from .utils import DebouncedLogger


class ToolManager:
    def __init__(self):
        self.logger = DebouncedLogger(interval=5.0)
        self.tools = {}

    def register_tool(self, tool_name: str, tool_func: callable):
        """Register a tool function with a name."""
        self.tools[tool_name] = tool_func
        self.logger.debug(f"Registered tool: {tool_name}")

    def execute_tool(self, tool_name: str, input_: str) -> str:
        """Execute a registered tool with the given input."""
        try:
            if tool_name in self.tools:
                tool_func = self.tools[tool_name]
                result = tool_func(input_)
                self.logger.debug(f"Executed tool: {tool_name} with input: {input_}")
                return result
            else:
                self.logger.error(f"Tool not found: {tool_name}")
                return f"Tool not found: {tool_name}"
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool {tool_name}: {e}"
