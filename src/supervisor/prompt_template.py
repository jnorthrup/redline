from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AgentContext:
    role: str
    abilities: List[str]
    memory_access: bool
    token_limit: int
    reward_context: Dict[str, Any]


@dataclass
class PromptTemplate:
    system_context: str
    agent_context: AgentContext
    status_line: str
    context_window: str

    def build_prompt(self) -> str:
        return f"""
# System Context
{self.system_context}

# Agent Role & Capabilities
Role: {self.agent_context.role}
Abilities: {', '.join(self.agent_context.abilities)}
Memory Access: {'Enabled' if self.agent_context.memory_access else 'Disabled'}
Token Limit: {self.agent_context.token_limit}

# Current Status
{self.status_line}

# Context Window
{self.context_window}

# Reward Context
{self.agent_context.reward_context}
"""
