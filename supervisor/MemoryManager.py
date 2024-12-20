"""
Module for memory management with file-based persistence and concurrency support.
"""

import fcntl
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from redline.supervisor.utils import DebouncedLogger


class MemoryManager:
    """Class to handle memory management operations with file persistence."""

    def __init__(self):
        """Initialize the MemoryManager with default settings."""
        self.logger = DebouncedLogger(interval=5.0)
        self.storage_dir = "memory_storage"
        self.cleanup_threshold = timedelta(days=7)  # Cleanup entries older than 7 days
        self.max_retries = 3
        self.retry_delay = 0.5  # seconds
        os.makedirs(self.storage_dir, exist_ok=True)
        self.logger.debug("MemoryManager initialized with file persistence")

    def _get_storage_path(self, key: str) -> str:
        """Get the storage file path for a given key"""
        return os.path.join(self.storage_dir, f"{key}.json")

    def _load_storage(self, key: str, retries: int = 0) -> List[Dict[str, Any]]:
        """Load data from storage file with proper locking and retries"""
        storage_path = self._get_storage_path(key)
        if not os.path.exists(storage_path):
            return []

        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                # Get an exclusive lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    return json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error reading storage for key {key}: {e}")
            if retries < self.max_retries:
                time.sleep(self.retry_delay)
                return self._load_storage(key, retries + 1)
            return []

    def store(self, key: str, data: Dict[str, Any], retries: int = 0) -> None:
        """Store data with timestamp and file persistence"""
        storage_path = self._get_storage_path(key)

        # Add timestamp to data
        data_with_timestamp = {**data, "_stored_at": datetime.now().isoformat()}

        try:
            # Create file if it doesn't exist
            if not os.path.exists(storage_path):
                with open(storage_path, "w", encoding="utf-8") as f:
                    json.dump([], f)

            # Load existing data with exclusive lock
            with open(storage_path, "r+", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []

                    # Append new data
                    existing_data.append(data_with_timestamp)

                    # Write back to file
                    f.seek(0)
                    f.truncate()
                    json.dump(existing_data, f, indent=2)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            self.logger.debug(f"Stored data for key: {key}")
        except Exception as e:
            self.logger.error(f"Error storing data for key {key}: {str(e)}")
            if retries < self.max_retries:
                time.sleep(self.retry_delay)
                self.store(key, data, retries + 1)
            else:
                raise

    def get(self, key: str) -> List[Dict[str, Any]]:
        """Retrieve data for given key from file storage"""
        return self._load_storage(key)

    def clear(self, key: str, retries: int = 0) -> None:
        """Clear data for given key from file storage"""
        storage_path = self._get_storage_path(key)
        if os.path.exists(storage_path):
            try:
                with open(storage_path, "w", encoding="utf-8") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump([], f)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                self.logger.debug(f"Cleared data for key: {key}")
            except Exception as e:
                self.logger.error(f"Error clearing data for key {key}: {str(e)}")
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    self.clear(key, retries + 1)
                else:
                    raise

    def cleanup_old_data(self) -> None:
        """Clean up old data entries exceeding the cleanup threshold"""
        now = datetime.now()
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json"):
                continue

            key = filename[:-5]  # Remove .json extension
            data = self.get(key)

            # Filter out old entries
            filtered_data = [
                entry
                for entry in data
                if datetime.fromisoformat(entry["_stored_at"])
                > (now - self.cleanup_threshold)
            ]

            # If data was filtered, update the storage
            if len(filtered_data) < len(data):
                try:
                    with open(self._get_storage_path(key), "w", encoding="utf-8") as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                        try:
                            json.dump(filtered_data, f, indent=2)
                        finally:
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    self.logger.debug(f"Cleaned up old data for key: {key}")
                except Exception as e:
                    self.logger.error(
                        f"Error cleaning up old data for key {key}: {str(e)}"
                    )

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "total_keys": 0,
            "total_entries": 0,
            "storage_size": 0,
            "oldest_entry": None,
            "newest_entry": None,
        }

        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json"):
                continue

            stats["total_keys"] += 1
            filepath = os.path.join(self.storage_dir, filename)
            stats["storage_size"] += os.path.getsize(filepath)

            data = self.get(filename[:-5])
            stats["total_entries"] += len(data)

            for entry in data:
                entry_time = datetime.fromisoformat(entry["_stored_at"])
                if stats["oldest_entry"] is None or entry_time < stats["oldest_entry"]:
                    stats["oldest_entry"] = entry_time
                if stats["newest_entry"] is None or entry_time > stats["newest_entry"]:
                    stats["newest_entry"] = entry_time

        return stats
