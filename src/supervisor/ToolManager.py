"""
Module for managing tools.

Mermaid interaction diagram for ToolManager:

```mermaid
classDiagram
    class ToolManager {
        +DebouncedLogger logger
        +Dict tools
        +register_tool(tool_name, tool_func)
        +execute_tool(tool_name, input_) 
        +list_tools() 
    }

    class DebouncedLogger {
        +interval: float
        +debug(message)
        +error(message)
    }

    class Tool {
        +callable function
    }

    ToolManager --> DebouncedLogger : uses
    ToolManager --> Tool : manages
    ToolManager : +Dict tools
    ToolManager : +register_tool(tool_name, tool_func)
    ToolManager : +execute_tool(tool_name, input_) 
    ToolManager : +list_tools()
```

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
                print(f"Executing tool: {tool_name} with input: {input_}")
                tool_func = self.tools[tool_name]
                result = tool_func(input_)
                print(f"Tool: {tool_name} execution complete.")
                self.logger.debug(f"Executed tool: {tool_name} with input: {input_}")
                return result
            else:
                self.logger.error(f"Tool not found: {tool_name}")
                return f"Tool not found: {tool_name}"
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool {tool_name}: {e}"
