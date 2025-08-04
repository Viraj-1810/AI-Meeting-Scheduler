from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from models import User, Message, Meeting, MeetingIntent

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        if not self.mongo_uri:
            raise ValueError("MONGO_URI not found in environment variables")
        
        # Configure MongoDB client with proper SSL settings for TLS handshake issues
        self.client = MongoClient(
            self.mongo_uri,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            ssl=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            tlsInsecure=True,
            directConnection=False,
            retryWrites=True,
            w='majority'
        )
        self.db = self.client["meeting_scheduler"]
        
        # Collections
        self.users = self.db["users"]
        self.messages = self.db["messages"]
        self.meetings = self.db["meetings"]
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            self.users.create_index("email", unique=True)
            
            # Messages collection indexes
            self.messages.create_index("timestamp")
            self.messages.create_index("email")
            
            # Meetings collection indexes
            self.meetings.create_index("date")
            self.meetings.create_index("participants")
            self.meetings.create_index("status")
            
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            self.client.admin.command('ping')
            print("✅ Database connection successful")
            return True
        except ServerSelectionTimeoutError as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    # User operations
    def create_user(self, name: str, email: str) -> Optional[str]:
        """Create a new user"""
        try:
            user_data = {
                "name": name,
                "email": email,
                "created_at": datetime.now()
            }
            result = self.users.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            print(f"⚠️ User with email {email} already exists")
            return None
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = self.users.find_one({"email": email})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            users = list(self.users.find({}))
            for user in users:
                user["id"] = str(user["_id"])
                del user["_id"]
            return users
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return []
    
    # Message operations
    def save_message(self, name: str, email: str, message: str) -> Optional[str]:
        """Save a new message"""
        try:
            message_data = {
                "name": name,
                "email": email,
                "message": message,
                "timestamp": datetime.now()
            }
            result = self.messages.insert_one(message_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return None
    
    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all messages with optional limit"""
        try:
            messages = list(self.messages.find({}).sort("timestamp", -1).limit(limit))
            for message in messages:
                message["id"] = str(message["_id"])
                del message["_id"]
            return messages[::-1]  # Reverse to show oldest first
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_messages_by_user(self, email: str) -> List[Dict[str, Any]]:
        """Get messages by specific user"""
        try:
            messages = list(self.messages.find({"email": email}).sort("timestamp", -1))
            for message in messages:
                message["id"] = str(message["_id"])
                del message["_id"]
            return messages[::-1]
        except Exception as e:
            print(f"❌ Error getting user messages: {e}")
            return []
    
    # Meeting operations
    def create_meeting(self, date: str, time: str, participants: List[str], 
                      title: str = None, description: str = None) -> Optional[str]:
        """Create a new meeting"""
        try:
            meeting_data = {
                "date": date,
                "time": time,
                "participants": participants,
                "title": title,
                "description": description,
                "status": "scheduled",
                "created_at": datetime.now()
            }
            result = self.meetings.insert_one(meeting_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error creating meeting: {e}")
            return None
    
    def get_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        try:
            meetings = list(self.meetings.find({}).sort("created_at", -1))
            for meeting in meetings:
                meeting["id"] = str(meeting["_id"])
                del meeting["_id"]
            return meetings
        except Exception as e:
            print(f"❌ Error getting meetings: {e}")
            return []
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        try:
            from bson import ObjectId
            meeting = self.meetings.find_one({"_id": ObjectId(meeting_id)})
            if meeting:
                meeting["id"] = str(meeting["_id"])
                del meeting["_id"]
            return meeting
        except Exception as e:
            print(f"❌ Error getting meeting: {e}")
            return None
    
    def update_meeting_status(self, meeting_id: str, status: str) -> bool:
        """Update meeting status"""
        try:
            from bson import ObjectId
            result = self.meetings.update_one(
                {"_id": ObjectId(meeting_id)},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating meeting status: {e}")
            return False
    
    # Analytics and reporting
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics"""
        try:
            total_messages = self.messages.count_documents({})
            total_users = self.users.count_documents({})
            total_meetings = self.meetings.count_documents({})
            
            # Get unique participants
            unique_participants = len(self.messages.distinct("email"))
            
            return {
                "total_messages": total_messages,
                "total_users": total_users,
                "total_meetings": total_meetings,
                "unique_participants": unique_participants
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def close_connection(self):
        """Close database connection"""
        try:
            self.client.close()
            print("✅ Database connection closed")
        except Exception as e:
            print(f"❌ Error closing connection: {e}")

# Global database instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
