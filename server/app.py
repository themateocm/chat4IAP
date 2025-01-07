#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from database import Database

class MessageHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for processing messages"""
    
    def __init__(self, *args, **kwargs):
        self.db = Database()
        # Set the directory containing static files
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, directory=directory, **kwargs)
    
    def do_GET(self):
        """Handle GET requests
        
        Serves static files and handles API endpoints:
        - /: Serves the main page
        - /messages: Returns list of messages
        """
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/messages':
            # Return messages as JSON
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            messages = self.db.get_messages()
            self.wfile.write(json.dumps({'messages': messages}).encode())
            return
        elif parsed_path.path == '/' or parsed_path.path == '':
            # Redirect to index.html
            self.path = '/templates/index.html'
            
        # Serve static files
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests
        
        Processes message submissions:
        - /messages: Accepts new messages
        """
        if self.path == '/messages':
            # Get message content
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                message_data = json.loads(post_data.decode('utf-8'))
                content = message_data.get('content')
                
                if not content:
                    raise ValueError("Message content is required")
                
                # Store message in database
                message_id = self.db.add_message(content)
                
                # Send success response
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'success', 'message': 'Message received', 'id': message_id}
                self.wfile.write(json.dumps(response).encode())
                
            except (json.JSONDecodeError, ValueError) as e:
                # Handle invalid JSON or missing content
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error = {'error': str(e)}
                self.wfile.write(json.dumps(error).encode())
        else:
            # Handle invalid endpoints
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error = {'error': 'Endpoint not found'}
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
