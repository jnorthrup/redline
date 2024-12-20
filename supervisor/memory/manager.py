import fcntl
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils import DebouncedLogger
from .git_storage import GitStorage


class MemoryManager:
    def __init__(self, storage_dir: str = "memory_storage"):
        self.logger = DebouncedLogger(interval=5.0)
        self.storage = GitStorage(storage_dir)
        self.logger.debug("MemoryManager initialized with git persistence")

    def store(self, key: str, data: Dict[str, Any]) -> None:
        """Store data with git versioning"""
        self.storage.store(key, data)

    def load(self, key: str, version: str = "HEAD") -> Optional[List[Dict[str, Any]]]:
        """Load data with optional version specification"""
        return self.storage.load(key, version)

    def get_history(self, key: str) -> List[Dict[str, Any]]:
        """Get version history for a key"""
        return self.storage.get_history(key)
