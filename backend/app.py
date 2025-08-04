from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
import re
import dateparser
from sqlite_db import get_sqlite_db_manager
from memory_db import get_memory_db_manager
from models import MessageCreate, MeetingCreate, MeetingIntent
from email_service import get_email_service
from demo_email_service import get_demo_email_service
from sample_data import load_sample_data, clear_sample_data, get_sample_conversation_summary
from simple_nlp import analyze_meeting_intent, suggest_meeting_times
from conversation_analyzer import get_conversation_analyzer

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask
app = Flask(__name__)
CORS(app)

# ✅ Initialize database manager
try:
    db_manager = get_sqlite_db_manager()
    if not db_manager.test_connection():
        raise Exception("Database connection failed")
    print("✅ SQLite database manager initialized successfully")
except Exception as e:
    print(f"⚠️ SQLite connection failed: {e}")
    print("🔄 Falling back to in-memory database for testing...")
    try:
        db_manager = get_memory_db_manager()
        print("✅ Memory database manager initialized successfully")
    except Exception as mem_e:
        print(f"❌ Memory database initialization failed: {mem_e}")
        raise mem_e

# ✅ Initialize email service
try:
    # Try real email service first
    email_service = get_email_service()
    if email_service.email_enabled:
        print("✅ Real email service initialized successfully")
    else:
        # Fall back to demo email service
        email_service = get_demo_email_service()
        print("✅ Demo email service initialized successfully")
except Exception as e:
    print(f"⚠️ Email service initialization failed: {e}")
    # Fall back to demo email service
    email_service = get_demo_email_service()
    print("✅ Demo email service initialized successfully")

# ✅ Load NLP
print("✅ Simplified NLP module loaded successfully")

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    """Health check endpoint"""
    try:
        stats = db_manager.get_chat_statistics()
        return jsonify({
            "message": "Backend running and connected to MongoDB Atlas!",
            "statistics": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    """Detailed health check"""
    try:
        db_status = db_manager.test_connection()
        db_type = "sqlite" if "SQLiteDatabaseManager" in str(type(db_manager)) else "memory"
        return jsonify({
            "status": "healthy" if db_status else "unhealthy",
            "database": f"{db_type}_connected" if db_status else f"{db_type}_disconnected",
            "email_service": "enabled" if email_service and email_service.email_enabled else "disabled",
            "nlp_model": "simplified",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Save chat message
@app.route("/message", methods=["POST"])
def save_message():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ["name", "email", "message"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Save message
        message_id = db_manager.save_message(
            name=data["name"],
            email=data["email"],
            message=data["message"]
        )
        
        if message_id:
            return jsonify({
                "status": "Message saved successfully",
                "message_id": message_id
            }), 201
        else:
            return jsonify({"error": "Failed to save message"}), 500
            
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get all chat messages
@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        limit = request.args.get("limit", 100, type=int)
        messages = db_manager.get_messages(limit=limit)
        return jsonify(messages)
    except Exception as e:
        print(f"❌ Error getting messages: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get messages by user
@app.route("/messages/user/<email>", methods=["GET"])
def get_messages_by_user(email):
    try:
        messages = db_manager.get_messages_by_user(email)
        return jsonify(messages)
    except Exception as e:
        print(f"❌ Error getting user messages: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get all users
@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = db_manager.get_all_users()
        return jsonify(users)
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Create user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.json
        if not data or not data.get("name") or not data.get("email"):
            return jsonify({"error": "Name and email are required"}), 400
        
        user_id = db_manager.create_user(
            name=data["name"],
            email=data["email"]
        )
        
        if user_id:
            return jsonify({
                "status": "User created successfully",
                "user_id": user_id
            }), 201
        else:
            return jsonify({"error": "Failed to create user"}), 500
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Enhanced meeting intent detection
def extract_meeting_details(chat_history):
    """
    Extract meeting details from chat history using simplified NLP
    """
    # Combine all messages into one text for analysis
    combined_text = " ".join([msg["message"] for msg in chat_history])
    
    # Use the simplified NLP function
    meeting_intent = analyze_meeting_intent(combined_text)
    
    # Add participants from chat history
    participants = set()
    for msg in chat_history:
        participants.add(msg["email"])
    
    # Update participants in the meeting intent
    meeting_intent.participants.extend(list(participants))
    meeting_intent.participants = list(set(meeting_intent.participants))  # Remove duplicates
    
    # Update missing_info based on what we actually have
    missing_info = []
    if not meeting_intent.suggested_date:
        missing_info.append("date")
    if not meeting_intent.suggested_time:
        missing_info.append("time")
    if not meeting_intent.participants:
        missing_info.append("participants")
    
    meeting_intent.missing_info = missing_info
    
    return meeting_intent

# ✅ Schedule meeting route with enhanced logic for multiple meetings
@app.route("/schedule", methods=["POST"])
def schedule_meeting():
    try:
        # Get chat history
        chat_history = db_manager.get_messages(limit=50)
        
        if not chat_history:
            return jsonify({
                "status": "No messages found",
                "message": "Please start a conversation first"
            }), 400

        # Use conversation analyzer to detect separate meeting contexts
        conversation_analyzer = get_conversation_analyzer()
        meeting_contexts = conversation_analyzer.extract_meeting_contexts(chat_history)
        
        if not meeting_contexts:
            # Fall back to original single meeting logic
            meeting_intent = extract_meeting_details(chat_history)
            
            if not meeting_intent.intent_detected:
                return jsonify({
                    "status": "No meeting intent detected",
                    "message": "No meeting scheduling intent found in the conversation"
                }), 400

            # If missing information, return what's needed
            if meeting_intent.missing_info:
                return jsonify({
                    "status": "Need more information",
                    "message": f"Please provide: {', '.join(meeting_intent.missing_info)}",
                    "missing_info": meeting_intent.missing_info,
                    "extracted_data": {
                        "dates": meeting_intent.extracted_dates,
                        "times": meeting_intent.extracted_times,
                        "participants": meeting_intent.participants
                    }
                }), 200

            # Create single meeting
            meeting_id = db_manager.create_meeting(
                date=meeting_intent.suggested_date,
                time=meeting_intent.suggested_time,
                participants=meeting_intent.participants
            )

            if meeting_id:
                meeting = db_manager.get_meeting_by_id(meeting_id)
                
                # Send confirmation emails
                if email_service:
                    email_sent = email_service.send_meeting_confirmation(
                        meeting, meeting_intent.participants
                    )
                    print(f"📧 Email confirmation sent: {email_sent}")
                else:
                    print("⚠️ Email service not available - skipping confirmation emails")
                
                return jsonify({
                    "status": "Meeting scheduled successfully",
                    "meeting_id": meeting_id,
                    "details": meeting,
                    "confidence": meeting_intent.confidence,
                    "email_sent": True if email_service else False
                }), 200
            else:
                return jsonify({"error": "Failed to schedule meeting"}), 500

        # Handle multiple meeting contexts
        scheduled_meetings = []
        total_confidence = 0
        
        for i, context in enumerate(meeting_contexts):
            # Extract meeting details for this context
            context_text = ' '.join([msg.get('message', '') for msg in context['messages']])
            meeting_intent = analyze_meeting_intent(context_text)
            
            # Use participants from context
            meeting_intent.participants = context['participants']
            
            # Use extracted times from context if available
            if context.get('extracted_times'):
                meeting_intent.suggested_time = context['extracted_times'][0]
            
            # Create meeting for this context
            meeting_id = db_manager.create_meeting(
                date=meeting_intent.suggested_date or "2025-08-04",  # Default date
                time=meeting_intent.suggested_time or "2:00 PM",  # Default time
                participants=meeting_intent.participants
            )
            
            if meeting_id:
                meeting = db_manager.get_meeting_by_id(meeting_id)
                scheduled_meetings.append(meeting)
                total_confidence += meeting_intent.confidence
                
                # Send confirmation emails for this meeting
                if email_service:
                    email_sent = email_service.send_meeting_confirmation(
                        meeting, meeting_intent.participants
                    )
                    print(f"📧 Email confirmation sent for meeting {i+1}: {email_sent}")
                else:
                    print(f"⚠️ Email service not available for meeting {i+1}")
        
        if scheduled_meetings:
            avg_confidence = total_confidence / len(scheduled_meetings)
            return jsonify({
                "status": "Multiple meetings scheduled successfully",
                "meetings": scheduled_meetings,
                "meeting_count": len(scheduled_meetings),
                "confidence": avg_confidence,
                "email_sent": True if email_service else False
            }), 200
        else:
            return jsonify({"error": "Failed to schedule any meetings"}), 500

    except Exception as e:
        print(f"❌ Error scheduling meeting: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get all meetings
@app.route("/meetings", methods=["GET"])
def get_meetings():
    try:
        meetings = db_manager.get_meetings()
        return jsonify(meetings)
    except Exception as e:
        print(f"❌ Error getting meetings: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get meeting by ID
@app.route("/meetings/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    try:
        meeting = db_manager.get_meeting_by_id(meeting_id)
        if meeting:
            return jsonify(meeting)
        else:
            return jsonify({"error": "Meeting not found"}), 404
    except Exception as e:
        print(f"❌ Error getting meeting: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Update meeting status
@app.route("/meetings/<meeting_id>/status", methods=["PUT"])
def update_meeting_status(meeting_id):
    try:
        data = request.json
        if not data or not data.get("status"):
            return jsonify({"error": "Status is required"}), 400
        
        success = db_manager.update_meeting_status(meeting_id, data["status"])
        if success:
            return jsonify({"status": "Meeting status updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update meeting status"}), 500
    except Exception as e:
        print(f"❌ Error updating meeting status: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Get statistics
@app.route("/statistics", methods=["GET"])
def get_statistics():
    try:
        stats = db_manager.get_chat_statistics()
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Test email service
@app.route("/test-email", methods=["POST"])
def test_email():
    try:
        data = request.json
        if not data or not data.get("email"):
            return jsonify({"error": "Email address is required"}), 400
        
        test_email = data["email"]
        
        if not email_service:
            return jsonify({
                "error": "Email service not available",
                "message": "Email service could not be initialized"
            }), 400
        
        # Test email connection
        if not email_service.test_connection():
            return jsonify({"error": "Email connection test failed"}), 500
        
        # Send test email
        test_meeting = {
            "title": "Test Meeting",
            "date": "2024-01-15",
            "time": "2:00 PM",
            "description": "This is a test meeting to verify email functionality"
        }
        
        email_sent = email_service.send_meeting_confirmation(
            test_meeting, [test_email]
        )
        
        if email_sent:
            return jsonify({
                "status": "Test email sent successfully",
                "message": f"Test email sent to {test_email}"
            }), 200
        else:
            return jsonify({"error": "Failed to send test email"}), 500
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Sample data management
@app.route("/load-sample-data", methods=["POST"])
def load_sample_data_endpoint():
    """Load sample conversations and meetings for demonstration"""
    try:
        success = load_sample_data()
        if success:
            return jsonify({
                "status": "Sample data loaded successfully",
                "message": "Sample conversations and meetings have been loaded"
            }), 200
        else:
            return jsonify({"error": "Failed to load sample data"}), 500
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/clear-sample-data", methods=["POST"])
def clear_sample_data_endpoint():
    """Clear all sample data from the database"""
    try:
        success = clear_sample_data()
        if success:
            return jsonify({
                "status": "Sample data cleared successfully",
                "message": "All sample data has been removed"
            }), 200
        else:
            return jsonify({"error": "Failed to clear sample data"}), 500
    except Exception as e:
        print(f"❌ Error clearing sample data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/sample-data-info", methods=["GET"])
def get_sample_data_info():
    """Get information about available sample data"""
    try:
        summary = get_sample_conversation_summary()
        return jsonify(summary)
    except Exception as e:
        print(f"❌ Error getting sample data info: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Run Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)