#!/usr/bin/env python3

import os
from typing import List, Dict, Optional
from datetime import datetime
import heapq
from dataclasses import dataclass
from github import Github, Repository, Commit
from dotenv import load_dotenv

@dataclass
class RepositoryConfig:
    owner: str
    name: str
    branch: str = "main"
    messages_path: str = "messages"

class RepositoryManager:
    def __init__(self):
        """Initialize the repository manager with GitHub token"""
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else Github()
        self.repositories: List[RepositoryConfig] = []
    
    def add_repository(self, owner: str, name: str, branch: str = "main", messages_path: str = "messages") -> None:
        """Add a repository to the list of repositories to monitor
        
        Args:
            owner (str): Repository owner/organization
            name (str): Repository name
            branch (str, optional): Branch to monitor. Defaults to "main".
            messages_path (str, optional): Path where messages are stored. Defaults to "messages".
        """
        config = RepositoryConfig(owner=owner, name=name, branch=branch, messages_path=messages_path)
        self.repositories.append(config)
    
    def get_messages(self, since: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Get messages from all configured repositories
        
        Args:
            since (datetime, optional): Only get messages after this time
            limit (int, optional): Maximum number of messages to return
            
        Returns:
            List[Dict]: List of messages sorted by timestamp
        """
        all_messages = []
        
        try:
            for repo_config in self.repositories:
                try:
                    repo = self.github.get_repo(f"{repo_config.owner}/{repo_config.name}")
                    messages = self._get_repository_messages(repo, repo_config, since)
                    all_messages.extend(messages)
                except Exception as e:
                    print(f"Error getting messages from {repo_config.owner}/{repo_config.name}: {e}")
                    continue
            
            # Sort messages by timestamp
            all_messages.sort(key=lambda x: x['timestamp'])
            
            # Return only the most recent messages up to the limit
            return all_messages[-limit:] if limit else all_messages
            
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
        finally:
            self.github.close()
    
    def _get_repository_messages(self, repo: Repository, config: RepositoryConfig, since: Optional[datetime] = None) -> List[Dict]:
        """Get messages from a specific repository
        
        Args:
            repo (Repository): GitHub repository object
            config (RepositoryConfig): Repository configuration
            since (datetime, optional): Only get messages after this time
            
        Returns:
            List[Dict]: List of messages from this repository
        """
        messages = []
        
        try:
            # Get commits that modified the messages directory
            commits = repo.get_commits(path=config.messages_path)
            
            for commit in commits:
                # Skip commits before 'since' if specified
                if since and commit.commit.author.date < since:
                    continue
                
                # Get the files modified in this commit
                for file in commit.files:
                    if file.filename.startswith(config.messages_path) and file.filename.endswith('.txt'):
                        try:
                            # Get the file content
                            content = repo.get_contents(file.filename, ref=commit.sha)
                            message_text = content.decoded_content.decode('utf-8')
                            
                            messages.append({
                                'id': commit.sha,
                                'content': message_text,
                                'timestamp': commit.commit.author.date.isoformat(),
                                'repository': f"{config.owner}/{config.name}",
                                'author': commit.commit.author.name,
                                'commit_hash': commit.sha
                            })
                        except Exception as e:
                            print(f"Error getting content for {file.filename}: {e}")
                            continue
            
            return messages
            
        except Exception as e:
            print(f"Error getting repository messages: {e}")
            return []
    
    def store_message(self, content: str, message_id: str) -> Optional[str]:
        """Store a message in all configured repositories
        
        Args:
            content (str): Message content
            message_id (str): Unique message identifier
            
        Returns:
            Optional[str]: Commit hash if successful, None otherwise
        """
        if not self.repositories:
            print("No repositories configured")
            return None
        
        # Use the first repository as the primary storage
        primary_repo = self.repositories[0]
        
        try:
            repo = self.github.get_repo(f"{primary_repo.owner}/{primary_repo.name}")
            
            # Create message file path
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{primary_repo.messages_path}/{timestamp}_{message_id}.txt"
            
            # Create commit message
            commit_message = f"Add message {message_id}"
            
            # Create or update file
            response = repo.create_file(
                path=filename,
                message=commit_message,
                content=content,
                branch=primary_repo.branch
            )
            
            return response["commit"].sha
            
        except Exception as e:
            print(f"Error storing message: {e}")
            return None
        finally:
            self.github.close()
    
    def push_repositories(self) -> Dict[str, str]:
        """Push all repositories to their remotes
        
        Returns:
            Dict[str, str]: Dictionary mapping repository names to status messages
        """
        results = {}
        
        for repo_config in self.repositories:
            try:
                repo = self.github.get_repo(f"{repo_config.owner}/{repo_config.name}")
                
                # Get the default branch reference
                ref = repo.get_git_ref(f"heads/{repo_config.branch}")
                
                results[f"{repo_config.owner}/{repo_config.name}"] = {
                    "status": "success",
                    "message": f"Successfully pushed to {repo_config.branch}",
                    "sha": ref.object.sha
                }
                
            except Exception as e:
                results[f"{repo_config.owner}/{repo_config.name}"] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return results
