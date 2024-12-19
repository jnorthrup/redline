from typing import Optional, Dict, Any
from .providers import LLMProvider
from .memory import MemoryManager
from .tools import ToolManager
from .message import MessageHandler
from .system_prompt import SystemPromptHandler

class Supervisor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.message_handler = MessageHandler()
        self.system_prompt_handler = SystemPromptHandler(self.message_handler)
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        self.current_provider: Optional[LLMProvider] = None
        self.standby_provider: Optional[LLMProvider] = None
        
    def set_active_provider(self, provider: LLMProvider, model_name: str):
        self.current_provider = provider
        self.active_model = model_name
        self.system_prompt_handler.update_system_prompt(self)
        
    def set_standby_provider(self, provider: LLMProvider):
        self.standby_provider = provider
