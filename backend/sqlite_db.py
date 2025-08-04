import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import threading
from models import User, Message, Meeting, MeetingIntent

class SQLiteDatabaseManager:
    """SQLite database manager for the meeting scheduler application"""
    
    def __init__(self, db_path: str = "meeting_scheduler.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._create_tables()
        print("✅ SQLite database initialized successfully")
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        return self._local.connection
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Meetings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    participants TEXT NOT NULL,  -- JSON string
                    description TEXT,
                    status TEXT DEFAULT 'scheduled',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_email ON messages(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)')
            
            conn.commit()
            print("✅ Database tables and indexes created successfully")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise e
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    # User operations
    def create_user(self, name: str, email: str) -> Optional[str]:
        """Create a new user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            return str(cursor.lastrowid)
        except sqlite3.IntegrityError:
            print(f"⚠️ User with email {email} already exists")
            return None
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": str(row[0]),
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3]
                }
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                {
                    "id": str(row[0]),
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return []
    
    # Message operations
    def save_message(self, name: str, email: str, message: str) -> Optional[str]:
        """Save a new message and auto-create user if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, check if user exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_exists = cursor.fetchone()
            
            # If user doesn't exist, create them
            if not user_exists:
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (name, email)
                )
                print(f"✅ Auto-created user: {name} ({email})")
            
            # Save the message
            cursor.execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message)
            )
            conn.commit()
            return str(cursor.lastrowid)
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return None
    
    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages with limit"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            # Reverse to show oldest first
            return [
                {
                    "id": str(row[0]),
                    "name": row[1],
                    "email": row[2],
                    "message": row[3],
                    "timestamp": row[4]
                }
                for row in reversed(rows)
            ]
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_messages_by_user(self, email: str) -> List[Dict[str, Any]]:
        """Get messages by user email"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE email = ? ORDER BY timestamp DESC",
                (email,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": str(row[0]),
                    "name": row[1],
                    "email": row[2],
                    "message": row[3],
                    "timestamp": row[4]
                }
                for row in reversed(rows)
            ]
        except Exception as e:
            print(f"❌ Error getting user messages: {e}")
            return []
    
    # Meeting operations
    def create_meeting(self, date: str, time: str, participants: List[str], 
                      title: str = None, description: str = None) -> Optional[str]:
        """Create a new meeting"""
        try:
            import json
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert participants list to JSON string
            participants_json = json.dumps(participants)
            
            cursor.execute(
                "INSERT INTO meetings (title, date, time, participants, description) VALUES (?, ?, ?, ?, ?)",
                (title or f"Meeting on {date}", date, time, participants_json, description)
            )
            conn.commit()
            return str(cursor.lastrowid)
        except Exception as e:
            print(f"❌ Error creating meeting: {e}")
            return None
    
    def get_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        try:
            import json
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                {
                    "id": str(row[0]),
                    "title": row[1],
                    "date": row[2],
                    "time": row[3],
                    "participants": json.loads(row[4]),
                    "description": row[5],
                    "status": row[6],
                    "created_at": row[7]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Error getting meetings: {e}")
            return []
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        try:
            import json
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": str(row[0]),
                    "title": row[1],
                    "date": row[2],
                    "time": row[3],
                    "participants": json.loads(row[4]),
                    "description": row[5],
                    "status": row[6],
                    "created_at": row[7]
                }
            return None
        except Exception as e:
            print(f"❌ Error getting meeting: {e}")
            return None
    
    def update_meeting_status(self, meeting_id: str, status: str) -> bool:
        """Update meeting status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE meetings SET status = ? WHERE id = ?",
                (status, meeting_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error updating meeting status: {e}")
            return False
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get total messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            # Get total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Get total meetings
            cursor.execute("SELECT COUNT(*) FROM meetings")
            total_meetings = cursor.fetchone()[0]
            
            # Get unique participants
            cursor.execute("SELECT COUNT(DISTINCT email) FROM messages")
            unique_participants = cursor.fetchone()[0]
            
            # Get last message timestamp
            cursor.execute("SELECT timestamp FROM messages ORDER BY timestamp DESC LIMIT 1")
            last_message = cursor.fetchone()
            last_message_time = last_message[0] if last_message else None
            
            return {
                "total_messages": total_messages,
                "total_users": total_users,
                "total_meetings": total_meetings,
                "unique_participants": unique_participants,
                "last_message": last_message_time
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                "total_messages": 0,
                "total_users": 0,
                "total_meetings": 0,
                "unique_participants": 0,
                "last_message": None
            }
    
    def close_connection(self):
        """Close database connection"""
        try:
            if hasattr(self._local, 'connection'):
                self._local.connection.close()
                delattr(self._local, 'connection')
            print("✅ Database connection closed")
        except Exception as e:
            print(f"❌ Error closing connection: {e}")

def get_sqlite_db_manager() -> SQLiteDatabaseManager:
    """Get SQLite database manager instance"""
    return SQLiteDatabaseManager() 