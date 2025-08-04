from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from models import User, Message, Meeting, MeetingIntent

class MemoryDatabaseManager:
    """Simple in-memory database for testing when MongoDB is not available"""
    
    def __init__(self):
        self.users = {}
        self.messages = []
        self.meetings = {}
        print("✅ Memory database initialized for testing")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        return True
    
    def _create_indexes(self):
        """No-op for memory database"""
        pass
    
    # User operations
    def create_user(self, name: str, email: str) -> Optional[str]:
        """Create a new user"""
        try:
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "name": name,
                "email": email,
                "created_at": datetime.now()
            }
            self.users[user_id] = user_data
            return user_id
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            for user in self.users.values():
                if user["email"] == email:
                    return user
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            return list(self.users.values())
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return []
    
    # Message operations
    def save_message(self, name: str, email: str, message: str) -> Optional[str]:
        """Save a new message and auto-create user if they don't exist"""
        try:
            # First, check if user exists
            user_exists = any(user["email"] == email for user in self.users.values())
            
            # If user doesn't exist, create them
            if not user_exists:
                user_id = str(uuid.uuid4())
                user_data = {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "created_at": datetime.now()
                }
                self.users[user_id] = user_data
                print(f"✅ Auto-created user: {name} ({email})")
            
            # Save the message
            message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "name": name,
                "email": email,
                "message": message,
                "timestamp": datetime.now()
            }
            self.messages.append(message_data)
            return message_id
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return None
    
    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages with limit"""
        try:
            sorted_messages = sorted(self.messages, key=lambda x: x["timestamp"], reverse=True)
            return sorted_messages[:limit]
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_messages_by_user(self, email: str) -> List[Dict[str, Any]]:
        """Get messages by user email"""
        try:
            user_messages = [msg for msg in self.messages if msg["email"] == email]
            return sorted(user_messages, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            print(f"❌ Error getting user messages: {e}")
            return []
    
    # Meeting operations
    def create_meeting(self, date: str, time: str, participants: List[str], 
                      title: str = None, description: str = None) -> Optional[str]:
        """Create a new meeting"""
        try:
            meeting_id = str(uuid.uuid4())
            meeting_data = {
                "id": meeting_id,
                "title": title or f"Meeting on {date}",
                "date": date,
                "time": time,
                "participants": participants,
                "description": description or "Meeting scheduled via AI assistant",
                "status": "scheduled",
                "created_at": datetime.now()
            }
            self.meetings[meeting_id] = meeting_data
            return meeting_id
        except Exception as e:
            print(f"❌ Error creating meeting: {e}")
            return None
    
    def get_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        try:
            return list(self.meetings.values())
        except Exception as e:
            print(f"❌ Error getting meetings: {e}")
            return []
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        try:
            return self.meetings.get(meeting_id)
        except Exception as e:
            print(f"❌ Error getting meeting: {e}")
            return None
    
    def update_meeting_status(self, meeting_id: str, status: str) -> bool:
        """Update meeting status"""
        try:
            if meeting_id in self.meetings:
                self.meetings[meeting_id]["status"] = status
                return True
            return False
        except Exception as e:
            print(f"❌ Error updating meeting status: {e}")
            return False
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics"""
        try:
            total_users = len(self.users)
            total_messages = len(self.messages)
            total_meetings = len(self.meetings)
            unique_participants = len(set(msg["email"] for msg in self.messages))
            
            return {
                "total_users": total_users,
                "total_messages": total_messages,
                "total_meetings": total_meetings,
                "unique_participants": unique_participants,
                "last_message": self.messages[-1]["timestamp"] if self.messages else None
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                "total_users": 0,
                "total_messages": 0,
                "total_meetings": 0,
                "unique_participants": 0,
                "last_message": None
            }
    
    def close_connection(self):
        """No-op for memory database"""
        pass

def get_memory_db_manager() -> MemoryDatabaseManager:
    """Get memory database manager instance"""
    return MemoryDatabaseManager() 