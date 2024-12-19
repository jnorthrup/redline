"""Centralized memory management for agents"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

@dataclass 
class Memory:
    """Memory store with bias correction"""
    data: Dict[str, Any] = field(default_factory=dict)
    bias: float = 1.0
    
class MemoryManager:
    """Manages memory access and persistence across agents"""
    
    def __init__(self):
        self._stores: Dict[str, Memory] = {}
        self._shared: Memory = Memory()
        
    def get_store(self, agent_id: str) -> Memory:
        """Get memory store for an agent"""
        if agent_id not in self._stores:
            self._stores[agent_id] = Memory()
        return self._stores[agent_id]
        
    def get_shared(self) -> Memory:
        """Get shared memory store"""
        return self._shared
        
    def update_bias(self, agent_id: str, bias: float) -> None:
        """Update bias correction for an agent"""
        if agent_id in self._stores:
            self._stores[agent_id].bias = bias
            
    def clear(self, agent_id: Optional[str] = None) -> None:
        """Clear memory store(s)"""
        if agent_id:
            if agent_id in self._stores:
                self._stores[agent_id].data.clear()
        else:
            self._stores.clear()
            self._shared.data.clear()
