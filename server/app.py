#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse

class MessageHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for processing messages"""
    
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
            # TODO: Implement actual message fetching
            messages = {'messages': []}
            self.wfile.write(json.dumps(messages).encode())
            return
            
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
                # TODO: Implement message storage
                
                # Send success response
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'success', 'message': 'Message received'}
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                # Handle invalid JSON
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error = {'error': 'Invalid JSON'}
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
        print(f"Serving at port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
