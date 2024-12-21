from typing import Optional

from .providers import LLMProvider
from .providers.generic import GenericProvider


class ProviderManager:
    def __init__(self):
        self.current_provider: Optional[LLMProvider] = None
        self.standby_provider: Optional[LLMProvider] = None

    def set_active_provider(self, provider: LLMProvider, model_name: str):
        self.current_provider = provider
        self.active_model = model_name

    def set_standby_provider(self, provider: LLMProvider):
        self.standby_provider = provider
