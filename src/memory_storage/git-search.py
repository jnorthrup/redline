#!/usr/bin/env python3
import argparse
import re
import sqlite3
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple


class GitTextSearch:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.conn = self._setup_db()

    def _setup_db(self) -> sqlite3.Connection:
        """Initialize SQLite database for search index"""
        conn = sqlite3.connect(":memory:")  # Can be changed to persistent storage
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS text_index (
                commit_hash TEXT,
                file_path TEXT,
                line_number INTEGER,
                content TEXT,
                commit_date TEXT,
                author TEXT,
                PRIMARY KEY (commit_hash, file_path, line_number)
            )
        """
        )
        return conn

    def build_index(self, branch: str = "HEAD") -> None:
        """Build search index from git history"""
        # Get all commits
        commits = self._get_commits(branch)

        for commit in commits:
            files = self._get_files_at_commit(commit)
            for file_path in files:
                content = self._get_file_content(commit, file_path)
                if content:
                    self._index_content(commit, file_path, content)

    def _get_commits(self, branch: str) -> List[str]:
        """Get all commit hashes in reverse chronological order"""
        cmd = ["git", "-C", self.repo_path, "rev-list", "--all"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip().split("\n")

    def _get_files_at_commit(self, commit: str) -> List[str]:
        """Get list of files in a commit"""
        cmd = ["git", "-C", self.repo_path, "ls-tree", "-r", commit, "--name-only"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip().split("\n")

    def _get_file_content(self, commit: str, file_path: str) -> str:
        """Get content of file at specific commit"""
        cmd = ["git", "-C", self.repo_path, "show", f"{commit}:{file_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else None

    def _get_commit_info(self, commit: str) -> Tuple[str, str]:
        """Get commit date and author"""
        cmd = ["git", "-C", self.repo_path, "show", "-s", "--format=%ai|%an", commit]
        result = subprocess.run(cmd, capture_output=True, text=True)
        date, author = result.stdout.strip().split("|")
        return date, author

    def _index_content(self, commit: str, file_path: str, content: str) -> None:
        """Index file content with commit information"""
        date, author = self._get_commit_info(commit)

        for line_num, line in enumerate(content.split("\n"), 1):
            self.conn.execute(
                """
                INSERT OR REPLACE INTO text_index
                (commit_hash, file_path, line_number, content, commit_date, author)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (commit, file_path, line_num, line, date, author),
            )

        self.conn.commit()

    def search(self, query: str, context_lines: int = 2) -> List[Dict]:
        """
        Search for text across all indexed content
        Returns matches with surrounding context
        """
        results = []
        cursor = self.conn.execute(
            """
            SELECT commit_hash, file_path, line_number, content, commit_date, author
            FROM text_index
            WHERE content LIKE ?
            ORDER BY commit_date DESC
        """,
            (f"%{query}%",),
        )

        for row in cursor:
            commit, file_path, line_num, content, date, author = row

            # Get context lines
            context = self._get_context(commit, file_path, line_num, context_lines)

            results.append(
                {
                    "commit": commit,
                    "file": file_path,
                    "line": line_num,
                    "content": content,
                    "context": context,
                    "date": date,
                    "author": author,
                }
            )

        return results

    def _get_context(
        self, commit: str, file_path: str, line_num: int, context_lines: int
    ) -> List[Tuple[int, str]]:
        """Get surrounding lines for context"""
        start_line = max(1, line_num - context_lines)
        end_line = line_num + context_lines

        cursor = self.conn.execute(
            """
            SELECT line_number, content
            FROM text_index
            WHERE commit_hash = ?
            AND file_path = ?
            AND line_number BETWEEN ? AND ?
            ORDER BY line_number
        """,
            (commit, file_path, start_line, end_line),
        )

        return [(ln, content) for ln, content in cursor]

    def regex_search(self, pattern: str, context_lines: int = 2) -> List[Dict]:
        """Search using regular expressions"""
        results = []
        regex = re.compile(pattern)

        cursor = self.conn.execute("SELECT * FROM text_index")
        for row in cursor:
            commit, file_path, line_num, content, date, author = row
            if regex.search(content):
                context = self._get_context(commit, file_path, line_num, context_lines)
                results.append(
                    {
                        "commit": commit,
                        "file": file_path,
                        "line": line_num,
                        "content": content,
                        "context": context,
                        "date": date,
                        "author": author,
                    }
                )

        return results


def main():
    parser = argparse.ArgumentParser(description="Git repository full-text search")
    parser.add_argument("repo_path", help="Path to git repository")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--context", type=int, default=2, help="Number of context lines"
    )
    parser.add_argument(
        "--regex", action="store_true", help="Use regular expression search"
    )

    args = parser.parse_args()

    searcher = GitTextSearch(args.repo_path)
    searcher.build_index()

    results = (
        searcher.regex_search(args.query, args.context)
        if args.regex
        else searcher.search(args.query, args.context)
    )

    for result in results:
        print(f"\nCommit: {result['commit']}")
        print(f"File: {result['file']}")
        print(f"Author: {result['author']}")
        print(f"Date: {result['date']}")
        print("Context:")
        for line_num, line in result["context"]:
            prefix = ">" if line_num == result["line"] else " "
            print(f"{prefix} {line_num:4d} | {line}")
        print("-" * 80)


if __name__ == "__main__":
    main()
