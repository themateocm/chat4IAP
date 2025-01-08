#!/usr/bin/env python3

import os
import json
from datetime import datetime
from github import Github
from pathlib import Path
import subprocess
from typing import Optional

class GitManager:
    def __init__(self, messages_dir: str = "messages", github_api: Optional[Github] = None):
        """Initialize GitManager
        
        Args:
            messages_dir (str): Directory to store message files
            github_api (Github, optional): Github API instance for testing
        """
        self.messages_dir = messages_dir
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('REPOSITORY_NAME', 'chat4IAP')
        self.github_username = os.getenv('GITHUB_USERNAME')
        
        if not all([self.github_token, self.github_username]) and github_api is None:
            raise ValueError("GitHub credentials not found in environment variables")
        
        # Allow injection of Github API instance for testing
        self.g = github_api if github_api is not None else Github(self.github_token)
        
        if github_api is not None:
            self.repo = None  # Skip repo initialization for testing
        else:
            self.repo = self.g.get_user().get_repo(self.repo_name)
        
        # Create messages directory if it doesn't exist
        os.makedirs(self.messages_dir, exist_ok=True)
    
    def create_message_file(self, content: str, message_id: int) -> str:
        """Create a file containing the message
        
        Args:
            content (str): Message content
            message_id (int): Message ID from database
            
        Returns:
            str: Path to created file
        """
        timestamp = datetime.utcnow().isoformat()
        filename = f"message_{message_id}_{timestamp}.json"
        filepath = os.path.join(self.messages_dir, filename)
        
        message_data = {
            'id': message_id,
            'content': content,
            'timestamp': timestamp
        }
        
        with open(filepath, 'w') as f:
            json.dump(message_data, f, indent=2)
        
        return filepath
    
    def commit_and_push(self, filepath: str, message: str) -> Optional[str]:
        """Commit and push a file to GitHub
        
        Args:
            filepath (str): Path to file to commit
            message (str): Commit message
            
        Returns:
            Optional[str]: Commit hash if successful, None otherwise
        """
        try:
            # Read file content
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Get relative path from repo root
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            relative_path = os.path.relpath(filepath, repo_root)
            
            # Create or update file in GitHub
            result = self.repo.create_file(
                path=relative_path,
                message=message,
                content=content,
                branch="master"
            )
            
            return result['commit'].sha[:7] if result else None
            
        except Exception as e:
            print(f"Error in GitHub operations: {e}")
            return None
    
    def store_message(self, content: str, message_id: int) -> Optional[str]:
        """Store a message in a file and push to GitHub
        
        Args:
            content (str): Message content
            message_id (int): Message ID from database
            
        Returns:
            Optional[str]: Commit hash if successful, None otherwise
        """
        try:
            filepath = self.create_message_file(content, message_id)
            commit_message = f"Add message {message_id}"
            commit_hash = self.commit_and_push(filepath, commit_message)
            return commit_hash
            
        except Exception as e:
            print(f"Error storing message: {e}")
            return None
