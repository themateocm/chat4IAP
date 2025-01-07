#!/usr/bin/env python3

import os
import json
from datetime import datetime
from github import Github
from pathlib import Path
import subprocess
from typing import Optional

class GitManager:
    def __init__(self, messages_dir: str = "messages"):
        """Initialize GitManager
        
        Args:
            messages_dir (str): Directory to store message files
        """
        self.messages_dir = messages_dir
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('REPOSITORY_NAME', 'chat4IAP')
        self.github_username = os.getenv('GITHUB_USERNAME')
        
        if not all([self.github_token, self.github_username]):
            raise ValueError("GitHub credentials not found in environment variables")
        
        self.g = Github(self.github_token)
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
            # Stage the file
            subprocess.run(['git', 'add', filepath], check=True)
            
            # Create commit
            commit_process = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract commit hash from commit message
            commit_hash = None
            for line in commit_process.stdout.split('\n'):
                if line.startswith('[master') or line.startswith('[main'):
                    commit_hash = line.split()[1]
                    break
            
            # Push to remote
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            print(f"Error in Git operations: {e}")
            print(f"Command output: {e.output if hasattr(e, 'output') else 'No output'}")
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
