import datetime
import os
from typing import Any, Dict, List

import git

from .base import Agent


class ExecutionAgent(Agent):
    """Action execution agent"""

    def __init__(self):
        super().__init__()
        self._current_step = 0
        self._observations = []
        self._repo = None

    def process(self, plan_data: Dict[str, Any]) -> None:
        """
        Execute planned actions and collect observations
        """
        plan = plan_data["plan"]
        tools = plan_data["tools"]

        for step in plan:
            # Execute command
            result = self._execute_command(step, tools)

            # Collect observation
            observation = self._collect_observation(result)
            self._observations.append(observation)

            # Update memory
            self._update_memory(observation)

            # Handoff to feedback agent
            self.handoff_downstream(observation)

    def _execute_command(self, step: Dict, tools: List[str]) -> Any:
        """Execute a single command"""
        command = step.get("command")
        if command == "git_backup":
            return self._git_backup(step.get("params", {}))
        # Implementation specific to execution environment
        pass

    def _git_backup(self, params: Dict) -> Dict:
        """Perform git backup operations"""
        try:
            repo_path = params.get("repo_path", os.getcwd())
            remote_url = params.get("remote_url")
            branch = params.get("branch", "main")
            commit_msg = params.get("commit_message", "Automated backup commit")

            if not self._repo:
                try:
                    self._repo = git.Repo(repo_path)
                except git.exc.InvalidGitRepositoryError:
                    self._repo = git.Repo.init(repo_path)

            # Configure backup remote
            if remote_url:
                if "backup" in [r.name for r in self._repo.remotes]:
                    backup_remote = self._repo.remotes.backup
                    if backup_remote.url != remote_url:
                        backup_remote.set_url(remote_url)
                else:
                    self._repo.create_remote("backup", remote_url)

            # Stage changes
            untracked = self._repo.untracked_files
            if untracked:
                self._repo.index.add(untracked)

            modified = [item.a_path for item in self._repo.index.diff(None)]
            if modified:
                self._repo.index.add(modified)

            # Commit if there are changes
            if self._repo.is_dirty(untracked_files=True) or untracked or modified:
                commit = self._repo.index.commit(commit_msg)

                # Push to backup remote
                if remote_url:
                    self._repo.remotes.backup.push(branch)

                return {
                    "status": "success",
                    "message": "Git backup completed successfully",
                    "details": {
                        "commit_hash": commit.hexsha,
                        "files_changed": len(modified) + len(untracked),
                        "branch": branch,
                    },
                }

            return {
                "status": "success",
                "message": "No changes to backup",
                "details": {"files_changed": 0, "branch": branch},
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "details": {"error_type": type(e).__name__, "repo_path": repo_path},
            }

    def _collect_observation(self, result: Any) -> Dict:
        """Collect and format execution observation"""
        observation = {
            "timestamp": str(datetime.datetime.now()),
            "step": self._current_step,
            "result": result,
        }

        if isinstance(result, dict) and result.get("status") == "error":
            observation["error"] = True
            observation["requires_attention"] = True

        return observation

    def _update_memory(self, observation: Dict) -> None:
        """Update agent memory with new observation"""
        if "observations" not in self._memory.data:
            self._memory.data["observations"] = []
        self._memory.data["observations"].append(observation)
