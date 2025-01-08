#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "messages.db"):
        """Initialize database connection
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.initialize_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Create a database connection
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_path)
    
    def initialize_db(self):
        """Create the database and messages table if they don't exist"""
        try:
            with self.get_connection() as conn:
                # Read schema file
                with open('schema.sql', 'r') as f:
                    schema = f.read()
                
                # Execute schema
                conn.executescript(schema)
                conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def add_message(self, content: str, git_commit_hash: Optional[str] = None) -> int:
        """Add a new message to the database
        
        Args:
            content (str): Message content
            git_commit_hash (str, optional): Associated git commit hash
            
        Returns:
            int: ID of the inserted message
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                timestamp = datetime.utcnow().isoformat()
                
                cursor.execute(
                    """
                    INSERT INTO messages (content, timestamp, git_commit_hash)
                    VALUES (?, ?, ?)
                    """,
                    (content, timestamp, git_commit_hash)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error adding message: {e}")
            raise
    
    def get_messages(self, limit: int = 100) -> List[Dict]:
        """Retrieve messages from the database
        
        Args:
            limit (int): Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages with their metadata
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, content, timestamp, git_commit_hash
                    FROM messages
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row[0],
                        'content': row[1],
                        'timestamp': row[2],
                        'git_commit_hash': row[3]
                    })
                
                return messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            raise
    
    def get_all_messages(self) -> List[Dict]:
        """Retrieve all messages from the database
        
        Returns:
            List[Dict]: List of messages, each containing id, content, timestamp, and git_commit_hash
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, content, timestamp, git_commit_hash
                    FROM messages
                    ORDER BY timestamp DESC
                """)
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row[0],
                        'content': row[1],
                        'timestamp': row[2],
                        'git_commit_hash': row[3]
                    })
                
                return messages
                
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            raise
    
    def update_commit_hash(self, message_id: int, git_commit_hash: str):
        """Update the git commit hash for a message
        
        Args:
            message_id (int): Message ID
            git_commit_hash (str): Git commit hash to associate with the message
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    UPDATE messages
                    SET git_commit_hash = ?
                    WHERE id = ?
                    """,
                    (git_commit_hash, message_id)
                )
                conn.commit()
        except Exception as e:
            print(f"Error updating commit hash: {e}")
            raise

if __name__ == "__main__":
    # Initialize the database
    db = Database()
    print("Database initialized successfully")
