"""Git-based storage implementation for memory management."""

import os
import json
import subprocess
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..utils import DebouncedLogger

class GitStorage:
    """Handles git-based storage operations for memory persistence."""
    
    def __init__(self, storage_dir: str = "memory_storage"):
        self.logger = DebouncedLogger(interval=5.0)
        self.storage_dir = storage_dir
        self._init_storage()

    def _init_storage(self) -> None:
        """Initialize git storage directory and repository."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        if not os.path.exists(os.path.join(self.storage_dir, '.git')):
            self._run_git_command('init')
            # Set up git config
            self._run_git_command('config', 'user.name', "Memory Manager")
            self._run_git_command('config', 'user.email', "memory@redline.local")

    def _run_git_command(self, *args: str) -> Optional[str]:
        """Run a git command in the storage directory."""
        try:
            cmd = ['git', '-C', self.storage_dir] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Git command failed: {result.stderr}")
                return None
            return result.stdout.strip()
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return None

    def store(self, key: str, data: Dict[str, Any]) -> None:
        """Store data with git versioning."""
        file_path = os.path.join(self.storage_dir, f"{key}.json")
        
        # Add timestamp to data
        data_with_timestamp = {
            **data,
            "_stored_at": datetime.now().isoformat()
        }
        
        try:
            # Write data to file
            with open(file_path, 'w') as f:
                json.dump(data_with_timestamp, f, indent=2)
            
            # Stage and commit changes
            self._run_git_command('add', f"{key}.json")
            commit_msg = f"Update {key} memory store"
            self._run_git_command('commit', '-m', commit_msg)
            
            self.logger.debug(f"Stored and committed data for key: {key}")
        except Exception as e:
            self.logger.error(f"Error storing data for key {key}: {str(e)}")
            raise

    def load(self, key: str, version: str = 'HEAD') -> Optional[Dict[str, Any]]:
        """Load data from git storage at specified version."""
        try:
            file_path = f"{key}.json"
            content = self._run_git_command('show', f'{version}:{file_path}')
            if content:
                return json.loads(content)
            return None
        except Exception as e:
            self.logger.error(f"Error loading data for key {key}: {str(e)}")
            return None

    def get_history(self, key: str) -> List[Dict[str, Any]]:
        """Get version history for a key."""
        try:
            file_path = f"{key}.json"
            log = self._run_git_command('log', '--pretty=format:%H|%ai|%s', file_path)
            if not log:
                return []
                
            history = []
            for line in log.split('\n'):
                commit_hash, date, message = line.split('|')
                data = self.load(key, commit_hash)
                if data:
                    history.append({
                        'version': commit_hash,
                        'date': date,
                        'message': message,
                        'data': data
                    })
            return history
        except Exception as e:
            self.logger.error(f"Error getting history for key {key}: {str(e)}")
            return []
