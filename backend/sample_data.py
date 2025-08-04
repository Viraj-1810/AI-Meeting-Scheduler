from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlite_db import get_sqlite_db_manager

# Sample users
SAMPLE_USERS = [
    {"name": "Alice Johnson", "email": "alice@company.com"},
    {"name": "Bob Smith", "email": "bob@company.com"},
    {"name": "Carol Davis", "email": "carol@company.com"},
    {"name": "David Wilson", "email": "david@company.com"},
    {"name": "Emma Brown", "email": "emma@company.com"}
]

# Sample conversations with meeting intent
SAMPLE_CONVERSATIONS = [
    # Conversation 1: Team Standup Meeting
    [
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "Good morning team! How's everyone doing?"},
        {"name": "Bob Smith", "email": "bob@company.com", "message": "Morning Alice! I'm doing well, just finished the user authentication feature."},
        {"name": "Carol Davis", "email": "carol@company.com", "message": "Hi everyone! I'm working on the database optimization. Should we schedule a team standup meeting?"},
        {"name": "David Wilson", "email": "david@company.com", "message": "Great idea Carol! I'm available tomorrow at 10 for a meeting."},
        {"name": "Emma Brown", "email": "emma@company.com", "message": "I can join tomorrow at 10 AM too. Let's discuss the project progress."},
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "Perfect! Let's schedule the standup for tomorrow at 10 AM."}
    ],
    
    # Conversation 2: Project Review Meeting
    [
        {"name": "Bob Smith", "email": "bob@company.com", "message": "Hey team, I think we need to review the new feature implementation."},
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "Agreed Bob. When are you all available this week?"},
        {"name": "Carol Davis", "email": "carol@company.com", "message": "I'm free on Wednesday afternoon, around 2."},
        {"name": "David Wilson", "email": "david@company.com", "message": "Wednesday 2 PM works for me too."},
        {"name": "Emma Brown", "email": "emma@company.com", "message": "I can make Wednesday at 2 PM. Let's schedule the project review meeting then."}
    ],
    
    # Conversation 3: Client Meeting
    [
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "We have a new client project starting next week."},
        {"name": "Bob Smith", "email": "bob@company.com", "message": "Great! When should we meet to discuss the requirements?"},
        {"name": "Carol Davis", "email": "carol@company.com", "message": "I'm available Monday morning, around 9 AM."},
        {"name": "David Wilson", "email": "david@company.com", "message": "Monday 9 AM works for me. Let's schedule the client meeting."},
        {"name": "Emma Brown", "email": "emma@company.com", "message": "I can join Monday at 9 AM too. Should we prepare an agenda?"}
    ],
    
    # Conversation 4: Technical Discussion
    [
        {"name": "Bob Smith", "email": "bob@company.com", "message": "We need to discuss the API architecture changes."},
        {"name": "Carol Davis", "email": "carol@company.com", "message": "Good point Bob. When can we have a technical discussion?"},
        {"name": "David Wilson", "email": "david@company.com", "message": "I'm free today at 3 PM for a call."},
        {"name": "Emma Brown", "email": "emma@company.com", "message": "Today 3 PM works for me too."},
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "Perfect! Let's schedule the technical discussion for today at 3 PM."}
    ],
    
    # Conversation 5: Sprint Planning
    [
        {"name": "Alice Johnson", "email": "alice@company.com", "message": "It's time for our sprint planning meeting."},
        {"name": "Bob Smith", "email": "bob@company.com", "message": "When should we schedule it? I'm available Friday morning."},
        {"name": "Carol Davis", "email": "carol@company.com", "message": "Friday morning works for me too. How about 11 AM?"},
        {"name": "David Wilson", "email": "david@company.com", "message": "Friday 11 AM is perfect for me."},
        {"name": "Emma Brown", "email": "emma@company.com", "message": "I can make Friday at 11 AM. Let's schedule the sprint planning meeting."}
    ]
]

# Sample meetings (already scheduled)
SAMPLE_MEETINGS = [
    {
        "date": "2024-01-15",
        "time": "10:00 AM",
        "participants": ["alice@company.com", "bob@company.com", "carol@company.com", "david@company.com", "emma@company.com"],
        "title": "Weekly Team Standup",
        "description": "Daily standup to discuss progress and blockers",
        "status": "scheduled"
    },
    {
        "date": "2024-01-17",
        "time": "2:00 PM",
        "participants": ["alice@company.com", "bob@company.com", "carol@company.com", "david@company.com", "emma@company.com"],
        "title": "Project Review Meeting",
        "description": "Review the new feature implementation and discuss next steps",
        "status": "scheduled"
    },
    {
        "date": "2024-01-22",
        "time": "9:00 AM",
        "participants": ["alice@company.com", "bob@company.com", "carol@company.com", "david@company.com", "emma@company.com"],
        "title": "Client Project Kickoff",
        "description": "Initial meeting with new client to discuss project requirements",
        "status": "scheduled"
    }
]

def load_sample_data():
    """Load sample data into the database"""
    try:
        db_manager = get_sqlite_db_manager()
        
        print("🔄 Loading sample data...")
        
        # Load sample users
        print("📝 Loading sample users...")
        for user in SAMPLE_USERS:
            try:
                db_manager.create_user(user["name"], user["email"])
            except Exception as e:
                print(f"⚠️ User {user['name']} might already exist: {e}")
                continue
        
        # Load sample conversations
        print("💬 Loading sample conversations...")
        for conversation in SAMPLE_CONVERSATIONS:
            for message in conversation:
                try:
                    # Add some time delay between messages
                    timestamp = datetime.now() - timedelta(minutes=len(conversation) * 5)
                    db_manager.save_message(
                        name=message["name"],
                        email=message["email"],
                        message=message["message"]
                    )
                except Exception as e:
                    print(f"⚠️ Error saving message: {e}")
                    continue
        
        # Load sample meetings
        print("📅 Loading sample meetings...")
        for meeting in SAMPLE_MEETINGS:
            try:
                db_manager.create_meeting(
                    date=meeting["date"],
                    time=meeting["time"],
                    participants=meeting["participants"],
                    title=meeting["title"],
                    description=meeting["description"]
                )
            except Exception as e:
                print(f"⚠️ Error creating meeting: {e}")
                continue
        
        print("✅ Sample data loaded successfully!")
        
        # Print statistics
        stats = db_manager.get_chat_statistics()
        print(f"📊 Statistics: {stats['total_messages']} messages, {stats['total_users']} users, {stats['total_meetings']} meetings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def clear_sample_data():
    """Clear all sample data from the database"""
    try:
        db_manager = get_sqlite_db_manager()
        
        print("🗑️ Clearing sample data...")
        
        # Clear all tables using SQL
        conn = db_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM meetings")
        conn.commit()
        
        print("✅ Sample data cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing sample data: {e}")
        return False

def get_sample_conversation_summary():
    """Get a summary of available sample conversations"""
    return {
        "conversations": [
            {
                "id": 1,
                "title": "Team Standup Meeting",
                "description": "Team discusses daily progress and schedules a standup meeting",
                "participants": 5,
                "meeting_intent": True,
                "suggested_time": "Tomorrow at 10 AM"
            },
            {
                "id": 2,
                "title": "Project Review Meeting",
                "description": "Team needs to review new feature implementation",
                "participants": 5,
                "meeting_intent": True,
                "suggested_time": "Wednesday at 2 PM"
            },
            {
                "id": 3,
                "title": "Client Meeting",
                "description": "New client project discussion and requirements gathering",
                "participants": 5,
                "meeting_intent": True,
                "suggested_time": "Monday at 9 AM"
            },
            {
                "id": 4,
                "title": "Technical Discussion",
                "description": "API architecture changes discussion",
                "participants": 5,
                "meeting_intent": True,
                "suggested_time": "Today at 3 PM"
            },
            {
                "id": 5,
                "title": "Sprint Planning",
                "description": "Agile sprint planning meeting",
                "participants": 5,
                "meeting_intent": True,
                "suggested_time": "Friday at 11 AM"
            }
        ],
        "users": SAMPLE_USERS,
        "meetings": SAMPLE_MEETINGS
    }

if __name__ == "__main__":
    # Test loading sample data
    load_sample_data() 