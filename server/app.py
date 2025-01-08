#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from datetime import datetime
from typing import List, Dict
from urllib.parse import parse_qs, urlparse
from server.database import Database
from server.repository_manager import RepositoryManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Debug: Environment variables:")
print(f"GITHUB_TOKEN exists: {'GITHUB_TOKEN' in os.environ}")
print(f"GITHUB_USERNAME exists: {'GITHUB_USERNAME' in os.environ}")
print(f"REPOSITORY_NAME exists: {'REPOSITORY_NAME' in os.environ}")

class MessageHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for processing messages"""
    
    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.repo_manager = RepositoryManager()
        
        # Configure repositories
        # You can add more repositories here
        self.repo_manager.add_repository(
            owner="your-username",
            name="chat-messages-primary",
            branch="main",
            messages_path="messages"
        )
        self.repo_manager.add_repository(
            owner="your-username",
            name="chat-messages-secondary",
            branch="main",
            messages_path="messages"
        )
        
        # Set the directory containing static files
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, directory=directory, **kwargs)
    
    def do_GET(self):
        """Handle GET requests
        
        Serves static files and handles API endpoints:
        - /: Serves the main page
        - /messages: Returns all messages from all repositories
        """
        if self.path == '/messages':
            try:
                # Get messages from both database and repositories
                db_messages = self.db.get_messages(limit=50)
                repo_messages = self.repo_manager.get_messages(limit=50)
                
                # Merge messages and sort by timestamp
                all_messages = db_messages + repo_messages
                all_messages.sort(key=lambda x: x['timestamp'])
                
                # Take the last 50 messages
                messages = all_messages[-50:]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(messages).encode())
                return
            except Exception as e:
                print(f"Error getting messages: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode())
                return
            
        if self.path == '/':
            # Serve the main page
            self.path = 'static/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            # Try to serve static files
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests
        
        Processes message submissions and repository operations:
        - /messages: Accepts new messages and stores them in both database and repositories
        - /push: Pushes all repositories to their remotes
        """
        if self.path == '/push':
            try:
                results = self.repo_manager.push_repositories()
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'success',
                    'message': 'Push operation completed',
                    'results': results
                }
                self.wfile.write(json.dumps(response).encode())
                return
                
            except Exception as e:
                print(f"Error pushing repositories: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode())
                return
                
        if self.path == '/messages':
            try:
                # Get content length
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                try:
                    # Parse JSON data
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'status': 'error', 'message': 'Invalid JSON format'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Check if content field exists and is not empty
                if 'content' not in data or not data['content'].strip():
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'status': 'error', 'message': 'Missing or empty content field'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Store message in database
                message_id = self.db.add_message(data['content'])
                
                # Store message in repositories
                commit_hash = self.repo_manager.store_message(data['content'], str(message_id))
                
                if commit_hash:
                    # Update the commit hash in database
                    self.db.update_commit_hash(message_id, commit_hash)
                
                # Send success response
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'success',
                    'message': 'Message received',
                    'id': message_id,
                    'commit_hash': commit_hash
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"Error processing message: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            # Handle invalid endpoints
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error = {'status': 'error', 'message': 'Endpoint not found'}
            self.wfile.write(json.dumps(error).encode())

def run_server(port=8080):
    """Start the HTTP server
    
    Args:
        port (int): Port number to listen on (default: 8080)
    """
    handler = MessageHandler
    
    # Allow the socket to be reused immediately after server restart
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server running at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
