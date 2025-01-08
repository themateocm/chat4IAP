import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime, timedelta
from server.app import MessageHandler
from http.server import SimpleHTTPRequestHandler
import io
from github import Github, Repository, Commit, GitAuthor
from urllib.parse import parse_qs, urlparse

class TestGitHubCommits(unittest.TestCase):
    def setUp(self):
        # Create mock request and client
        self.rfile = io.BytesIO()
        self.wfile = io.BytesIO()
        self.client_address = ('127.0.0.1', 12345)
        
        # Create a mock server
        self.server = MagicMock()
        self.server.server_name = 'test_server'
        self.server.server_port = 8080
        
        # Create a mock connection
        self.connection = MagicMock()
        self.connection.makefile = MagicMock()
        self.connection.makefile.side_effect = lambda mode, buffsize: self.rfile if mode == 'rb' else self.wfile
        
        # Create handler with mocked components
        self.handler = MessageHandler(self.connection, self.client_address, self.server)
        self.handler.wfile = self.wfile
        
        # Create mock commit data
        self.mock_commit_data = {
            'sha': 'abc123',
            'message': 'Test commit message',
            'author': 'Test Author',
            'date': datetime(2025, 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
        }
        
    def create_mock_commit(self, **kwargs):
        mock_commit = MagicMock(spec=Commit.Commit)
        mock_commit.sha = kwargs.get('sha', self.mock_commit_data['sha'])
        
        # Create nested mock objects
        mock_commit.commit = MagicMock()
        mock_commit.commit.message = kwargs.get('message', self.mock_commit_data['message'])
        mock_commit.commit.author = MagicMock(spec=GitAuthor.GitAuthor)
        mock_commit.commit.author.name = kwargs.get('author', self.mock_commit_data['author'])
        mock_commit.commit.author.date = kwargs.get('date', self.mock_commit_data['date'])
        
        return mock_commit
        
    @patch('server.app.Github')
    def test_fetch_github_commits(self, mock_github_class):
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        mock_commits_page = [self.create_mock_commit()]
        
        # Set up the chain of mock returns
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = mock_commits_page
        
        # Test fetching commits
        commits = self.handler.fetch_github_commits("test-owner", "test-repo")
        
        # Verify the mocks were called correctly
        mock_github.get_repo.assert_called_once_with("test-owner/test-repo")
        mock_repo.get_commits.assert_called_once()
        mock_commits_paginated.get_page.assert_called_once_with(0)
        
        # Assertions
        self.assertEqual(len(commits), 1)
        commit = commits[0]
        self.assertEqual(commit['sha'], self.mock_commit_data['sha'])
        self.assertEqual(commit['message'], self.mock_commit_data['message'])
        self.assertEqual(commit['author'], self.mock_commit_data['author'])
        self.assertEqual(commit['date'], self.mock_commit_data['date'].isoformat())
        
    @patch('server.app.Github')
    def test_fetch_github_commits_with_since(self, mock_github_class):
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        mock_commits_page = [self.create_mock_commit()]
        
        # Set up the chain of mock returns
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = mock_commits_page
        
        # Test fetching commits with since parameter
        commits = self.handler.fetch_github_commits(
            "test-owner", 
            "test-repo", 
            since="2024-12-31T00:00:00Z"
        )
        
        # Verify the mocks were called correctly
        mock_github.get_repo.assert_called_once_with("test-owner/test-repo")
        mock_repo.get_commits.assert_called_once()
        mock_commits_paginated.get_page.assert_called_once_with(0)
        
        # Assertions
        self.assertEqual(len(commits), 1)
        commit = commits[0]
        self.assertEqual(commit['sha'], self.mock_commit_data['sha'])

    @patch('server.app.Github')
    def test_fetch_github_commits_error(self, mock_github_class):
        # Setup mock to raise an exception
        mock_github = mock_github_class.return_value
        mock_github.get_repo.side_effect = Exception("Test error")
        
        # Test error handling
        commits = self.handler.fetch_github_commits("test-owner", "test-repo")
        
        # Should return empty list on error
        self.assertEqual(commits, [])
        
    @patch('server.app.Github')
    def test_fetch_github_commits_empty_repo(self, mock_github_class):
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        
        # Set up empty commits list
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = []
        
        # Test fetching commits from empty repo
        commits = self.handler.fetch_github_commits("test-owner", "test-repo")
        
        # Should return empty list
        self.assertEqual(commits, [])
        
    @patch('server.app.Github')
    def test_fetch_github_commits_pagination(self, mock_github_class):
        # Create multiple mock commits
        mock_commits = [
            self.create_mock_commit(sha=f'sha{i}', 
                                  message=f'Commit {i}',
                                  date=self.mock_commit_data['date'] + timedelta(days=i))
            for i in range(5)
        ]
        
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        
        # Set up mock returns
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = mock_commits
        
        # Test fetching commits with pagination
        commits = self.handler.fetch_github_commits("test-owner", "test-repo", per_page=3)
        
        # Should return only first 3 commits
        self.assertEqual(len(commits), 3)
        self.assertEqual(commits[0]['sha'], 'sha0')
        self.assertEqual(commits[2]['sha'], 'sha2')
        
    def test_api_endpoint_missing_params(self):
        # Test missing owner
        self.handler.path = "/api/commits?repo=test-repo"
        self.handler.send_error = MagicMock()
        self.handler.do_GET()
        self.handler.send_error.assert_called_with(400, "Missing owner or repo parameter")
        
        # Test missing repo
        self.handler.path = "/api/commits?owner=test-owner"
        self.handler.do_GET()
        self.handler.send_error.assert_called_with(400, "Missing owner or repo parameter")
        
    def test_api_endpoint_malformed_url(self):
        # Test malformed URL
        self.handler.path = "/api/commits?invalid=param"
        self.handler.send_error = MagicMock()
        self.handler.do_GET()
        self.handler.send_error.assert_called_with(400, "Missing owner or repo parameter")
        
    def test_api_endpoint(self):
        # Mock the handler's path and query parameters
        self.handler.path = "/api/commits?owner=test-owner&repo=test-repo"
        self.handler.send_response = MagicMock()
        self.handler.send_header = MagicMock()
        self.handler.end_headers = MagicMock()
        
        # Mock fetch_github_commits to return test data
        test_commits = [{
            'sha': self.mock_commit_data['sha'],
            'message': self.mock_commit_data['message'],
            'author': self.mock_commit_data['author'],
            'date': self.mock_commit_data['date'].isoformat()
        }]
        self.handler.fetch_github_commits = MagicMock(return_value=test_commits)
        
        # Call the GET handler
        self.handler.do_GET()
        
        # Verify response
        self.handler.send_response.assert_called_with(200)
        self.handler.send_header.assert_called_with('Content-Type', 'application/json')
        
        # Get the written response
        response = self.wfile.getvalue().decode()
        self.assertEqual(json.loads(response), test_commits)
        
    @patch('server.app.Github')
    def test_fetch_github_commits_with_multiline_message(self, mock_github_class):
        # Create mock commit with multiline message
        multiline_message = "First line\nSecond line\nThird line"
        mock_commit = self.create_mock_commit(message=multiline_message)
        
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        
        # Set up mock returns
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = [mock_commit]
        
        # Test fetching commit with multiline message
        commits = self.handler.fetch_github_commits("test-owner", "test-repo")
        
        # Verify multiline message is preserved
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]['message'], multiline_message)
        
    @patch('server.app.Github')
    def test_fetch_github_commits_with_special_chars(self, mock_github_class):
        # Create mock commit with special characters
        special_message = "Special chars: áéíóú ñ 你好 🚀 \u2713"
        mock_commit = self.create_mock_commit(message=special_message)
        
        # Create mock objects
        mock_github = mock_github_class.return_value
        mock_repo = MagicMock(spec=Repository.Repository)
        mock_commits_paginated = MagicMock()
        
        # Set up mock returns
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_commits.return_value = mock_commits_paginated
        mock_commits_paginated.get_page.return_value = [mock_commit]
        
        # Test fetching commit with special characters
        commits = self.handler.fetch_github_commits("test-owner", "test-repo")
        
        # Verify special characters are preserved
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]['message'], special_message)

if __name__ == '__main__':
    unittest.main()
