import unittest
import json
import os
import sqlite3
from unittest.mock import MagicMock, patch
import http.client
import threading
import time
from server.app import run_server, MessageHandler
from server.git_manager import GitManager

class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread"""
        # Mock GitManager before starting server
        cls.git_patcher = patch('server.app.GitManager')
        cls.mock_git_manager = cls.git_patcher.start()
        
        # Configure mock
        mock_instance = MagicMock()
        mock_instance.store_message.return_value = "abc123"
        cls.mock_git_manager.return_value = mock_instance
        
        # Start server
        cls.server_thread = threading.Thread(target=run_server, kwargs={'port': 8081})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        # Give the server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level mocks"""
        cls.git_patcher.stop()

    def setUp(self):
        """Set up test client"""
        self.conn = http.client.HTTPConnection('localhost', 8081)

    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()

    @patch('server.database.Database.add_message')
    def test_post_message(self, mock_add_message):
        """Test POST /messages endpoint"""
        # Set up mock
        mock_add_message.return_value = 123  # Mock message ID

        # Test data
        message_data = {
            "content": "Test message"
        }

        # Send POST request
        headers = {'Content-Type': 'application/json'}
        self.conn.request('POST', '/messages', json.dumps(message_data), headers)
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 201)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['id'], 123)
        self.assertEqual(response_data['commit_hash'], 'abc123')

        # Verify mocks were called correctly
        mock_add_message.assert_called_once_with("Test message")
        self.mock_git_manager.return_value.store_message.assert_called_once()

    def test_post_message_invalid_json(self):
        """Test POST /messages with invalid JSON"""
        # Send invalid JSON
        headers = {'Content-Type': 'application/json'}
        self.conn.request('POST', '/messages', "{invalid json", headers)
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 400)
        self.assertEqual(response_data['status'], 'error')

    def test_post_message_missing_content(self):
        """Test POST /messages with missing content field"""
        # Test data without content
        message_data = {}

        # Send POST request
        headers = {'Content-Type': 'application/json'}
        self.conn.request('POST', '/messages', json.dumps(message_data), headers)
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 400)
        self.assertEqual(response_data['status'], 'error')

    @patch('server.database.Database.get_all_messages')
    def test_get_messages(self, mock_get_messages):
        """Test GET /messages endpoint"""
        # Set up mock data
        mock_messages = [
            {
                'id': 1,
                'content': 'Test message 1',
                'timestamp': '2025-01-07T15:57:30-05:00',
                'git_commit_hash': 'abc123'
            },
            {
                'id': 2,
                'content': 'Test message 2',
                'timestamp': '2025-01-07T15:57:30-05:00',
                'git_commit_hash': 'def456'
            }
        ]
        mock_get_messages.return_value = mock_messages

        # Send GET request
        self.conn.request('GET', '/messages')
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['messages'], mock_messages)

        # Verify mock was called
        mock_get_messages.assert_called_once()

    @patch('server.database.Database.get_all_messages')
    def test_get_messages_empty(self, mock_get_messages):
        """Test GET /messages endpoint when there are no messages"""
        # Set up mock to return empty list
        mock_get_messages.return_value = []

        # Send GET request
        self.conn.request('GET', '/messages')
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['messages'], [])
        
        # Verify mock was called
        mock_get_messages.assert_called_once()

    @patch('server.database.Database.get_all_messages')
    def test_get_messages_database_error(self, mock_get_messages):
        """Test GET /messages endpoint when database error occurs"""
        # Set up mock to raise an exception
        mock_get_messages.side_effect = sqlite3.Error("Database error")

        # Send GET request
        self.conn.request('GET', '/messages')
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 500)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('message', response_data)
        
        # Verify mock was called
        mock_get_messages.assert_called_once()

    def test_get_messages_invalid_endpoint(self):
        """Test GET request to invalid endpoint"""
        # Send GET request to invalid endpoint
        self.conn.request('GET', '/invalid')
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 404)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Endpoint not found')

    @patch('server.database.Database.get_all_messages')
    def test_get_messages_verify_format(self, mock_get_messages):
        """Test GET /messages endpoint verifies message format"""
        # Set up mock data with all fields
        test_time = "2025-01-07T15:59:10-05:00"
        mock_messages = [
            {
                'id': 1,
                'content': 'First test message',
                'timestamp': test_time,
                'git_commit_hash': 'abc123'
            },
            {
                'id': 2,
                'content': 'Second test message',
                'timestamp': test_time,
                'git_commit_hash': None  # Test null commit hash
            }
        ]
        mock_get_messages.return_value = mock_messages

        # Send GET request
        self.conn.request('GET', '/messages')
        response = self.conn.getresponse()
        
        # Read and parse response
        response_data = json.loads(response.read().decode())

        # Verify response
        self.assertEqual(response.status, 200)
        self.assertEqual(response_data['status'], 'success')
        messages = response_data['messages']
        
        # Verify message format
        self.assertEqual(len(messages), 2)
        for i, message in enumerate(messages):
            self.assertIn('id', message)
            self.assertIn('content', message)
            self.assertIn('timestamp', message)
            self.assertIn('git_commit_hash', message)
            
            # Verify data types
            self.assertIsInstance(message['id'], int)
            self.assertIsInstance(message['content'], str)
            self.assertIsInstance(message['timestamp'], str)
            
            # Verify values match mock data
            self.assertEqual(message['id'], mock_messages[i]['id'])
            self.assertEqual(message['content'], mock_messages[i]['content'])
            self.assertEqual(message['timestamp'], test_time)
            self.assertEqual(message['git_commit_hash'], mock_messages[i]['git_commit_hash'])

if __name__ == '__main__':
    unittest.main()
