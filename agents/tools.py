"""Shared tools for agent operations"""

from typing import Any, Callable, Dict, List
import logging

class ToolRegistry:
    """Registry of available tools"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._permissions: Dict[str, List[str]] = {}
        
    def register(self, name: str, tool: Callable, 
                allowed_agents: Optional[List[str]] = None) -> None:
        """Register a tool"""
        self._tools[name] = tool
        if allowed_agents:
            self._permissions[name] = allowed_agents
            
    def get_tool(self, name: str, agent_id: str) -> Optional[Callable]:
        """Get tool if agent has permission"""
        if name not in self._tools:
            return None
            
        if name in self._permissions:
            if agent_id not in self._permissions[name]:
                logging.warning(f"Agent {agent_id} denied access to tool {name}")
                return None
                
        return self._tools[name]
        
    def list_tools(self, agent_id: str) -> List[str]:
        """List available tools for an agent"""
        available = []
        for name in self._tools:
            if name not in self._permissions or \
               agent_id in self._permissions[name]:
                available.append(name)
        return available
