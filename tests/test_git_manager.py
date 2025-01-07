#!/usr/bin/env python3

import unittest
import os
import json
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
from server.git_manager import GitManager
from github import Github
import subprocess

class TestGitManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a temporary messages directory
        self.test_messages_dir = "test_messages"
        os.makedirs(self.test_messages_dir, exist_ok=True)
        
        # Create mock Github API
        self.mock_github = MagicMock(spec=Github)
        
        # Initialize GitManager with test directory and mock API
        self.git_manager = GitManager(
            messages_dir=self.test_messages_dir,
            github_api=self.mock_github
        )
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove test directory
        if os.path.exists(self.test_messages_dir):
            shutil.rmtree(self.test_messages_dir)
    
    def test_initialization(self):
        """Test GitManager initialization"""
        self.assertEqual(self.git_manager.messages_dir, self.test_messages_dir)
        self.assertTrue(os.path.exists(self.test_messages_dir))
    
    def test_create_message_file(self):
        """Test message file creation"""
        content = "Test message"
        message_id = 1
        
        filepath = self.git_manager.create_message_file(content, message_id)
        
        # Check if file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['content'], content)
            self.assertEqual(data['id'], message_id)
            self.assertTrue('timestamp' in data)
    
    @patch('subprocess.run')
    def test_commit_and_push(self, mock_run):
        """Test commit and push functionality"""
        # Mock successful git commands
        mock_run.return_value = MagicMock(
            stdout='[master 1234567] Test commit\n',
            returncode=0
        )
        
        filepath = os.path.join(self.test_messages_dir, 'test.json')
        with open(filepath, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        commit_hash = self.git_manager.commit_and_push(filepath, "Test commit")
        
        # Verify git commands were called
        self.assertEqual(mock_run.call_count, 3)  # add, commit, push
        self.assertIsNotNone(commit_hash)
        
        # Verify the correct commands were called
        calls = mock_run.call_args_list
        self.assertEqual(calls[0][0][0], ['git', 'add', filepath])
        self.assertEqual(calls[1][0][0][:2], ['git', 'commit'])
        self.assertEqual(calls[2][0][0], ['git', 'push', 'origin', 'master'])
    
    @patch('subprocess.run')
    def test_commit_and_push_failure(self, mock_run):
        """Test commit and push failure handling"""
        # Mock git command failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git', "Git error")
        
        filepath = os.path.join(self.test_messages_dir, 'test.json')
        with open(filepath, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        commit_hash = self.git_manager.commit_and_push(filepath, "Test commit")
        
        # Verify failure handling
        self.assertIsNone(commit_hash)
    
    @patch.object(GitManager, 'commit_and_push')
    def test_store_message(self, mock_commit_and_push):
        """Test complete message storage process"""
        # Mock successful commit
        mock_commit_hash = "1234567"
        mock_commit_and_push.return_value = mock_commit_hash
        
        content = "Test message"
        message_id = 1
        
        commit_hash = self.git_manager.store_message(content, message_id)
        
        # Verify message storage
        self.assertEqual(commit_hash, mock_commit_hash)
        mock_commit_and_push.assert_called_once()
        
        # Verify file was created
        message_files = os.listdir(self.test_messages_dir)
        self.assertEqual(len(message_files), 1)
        
        # Check file content
        filepath = os.path.join(self.test_messages_dir, message_files[0])
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['content'], content)
            self.assertEqual(data['id'], message_id)

if __name__ == '__main__':
    unittest.main()
