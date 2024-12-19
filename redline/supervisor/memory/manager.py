import json
import os
import fcntl
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..utils import DebouncedLogger

class MemoryManager:
    def __init__(self, storage_dir: str = "memory_storage"):
        self.logger = DebouncedLogger(interval=5.0)
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.logger.debug("MemoryManager initialized with file persistence")

    def store(self, key: str, data: Dict[str, Any]) -> None:
        path = os.path.join(self.storage_dir, f"{key}.json")
        data_with_ts = {**data, "_stored_at": datetime.now().isoformat()}
        
        try:
            with open(path, 'r+' if os.path.exists(path) else 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    existing = json.load(f) if os.path.exists(path) else []
                    existing.append(data_with_ts)
                    f.seek(0)
                    f.truncate()
                    json.dump(existing, f, indent=2)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            self.logger.debug(f"Stored data for key: {key}")
        except Exception as e:
            self.logger.error(f"Failed to store data: {e}")
            raise

    def load(self, key: str) -> Optional[List[Dict[str, Any]]]:
        path = os.path.join(self.storage_dir, f"{key}.json")
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    try:
                        return json.load(f)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return None
