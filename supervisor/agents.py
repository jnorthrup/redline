from typing import Any, Dict, List

from redline.supervisor.tools import ToolA, ToolB, ToolC


class AgentOne:
    def __init__(
        self,
        tools: List[ToolA, ToolB],
        role: str,
        context_window: int,
        status_line: str,
        abilities: List[str],
        memory: Dict[str, Any],
        reward_credit: float,
        reward_function: Any,
        reward_context: Dict[str, Any],
    ):
        self.tools = tools
        self.role = role
        self.context_window = context_window
        self.status_line = status_line
        self.abilities = abilities
        self.memory = memory
        self.reward_credit = reward_credit
        self.reward_function = reward_function
        self.reward_context = reward_context


class AgentTwo:
    def __init__(
        self,
        tools: List[ToolB, ToolC],
        role: str,
        context_window: int,
        status_line: str,
        abilities: List[str],
        memory: Dict[str, Any],
        reward_credit: float,
        reward_function: Any,
        reward_context: Dict[str, Any],
    ):
        self.tools = tools
        self.role = role
        self.context_window = context_window
        self.status_line = status_line
        self.abilities = abilities
        self.memory = memory
        self.reward_credit = reward_credit
        self.reward_function = reward_function
        self.reward_context = reward_context
