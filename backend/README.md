# Meeting Scheduler Backend

A Flask-based REST API for an AI-powered meeting scheduling application.

## Features

- **Group Chat Management**: Store and retrieve multi-user conversations
- **Meeting Intent Detection**: AI-powered detection of meeting scheduling intent
- **Availability Extraction**: Extract dates, times, and participant availability
- **Meeting Scheduling**: Schedule meetings with participant consensus
- **Database Integration**: MongoDB Atlas integration with proper indexing
- **Enhanced NLP**: Advanced natural language processing for intent detection

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration

Copy `env_template.txt` to `.env` and configure:

```bash
cp env_template.txt .env
```

Edit `.env` with your MongoDB connection string and other settings.

### 4. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Checks
- `GET /` - Basic health check with statistics
- `GET /health` - Detailed health check

### Messages
- `POST /message` - Save a new message
- `GET /messages` - Get all messages (optional: `?limit=100`)
- `GET /messages/user/<email>` - Get messages by user

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users

### Meetings
- `POST /schedule` - Schedule a meeting based on chat history
- `GET /meetings` - Get all meetings
- `GET /meetings/<id>` - Get meeting by ID
- `PUT /meetings/<id>/status` - Update meeting status

### Analytics
- `GET /statistics` - Get chat statistics

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "created_at": "datetime"
}
```

### Messages Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "message": "string",
  "timestamp": "datetime"
}
```

### Meetings Collection
```json
{
  "_id": "ObjectId",
  "date": "string (YYYY-MM-DD)",
  "time": "string",
  "participants": ["string"],
  "title": "string (optional)",
  "description": "string (optional)",
  "status": "string (scheduled/cancelled/completed)",
  "created_at": "datetime"
}
```

## Meeting Intent Detection

The system uses advanced NLP to detect meeting scheduling intent:

### Keywords Detected
- **Meeting Intent**: meeting, schedule, call, zoom, meet, appointment, conference, discussion, sync, catch up, standup
- **Time Keywords**: available, free, busy, occupied, can't, cannot, tomorrow, today, next week, this week

### Extracted Information
- **Dates**: Using dateparser for flexible date parsing
- **Times**: Regex patterns for time extraction
- **Participants**: All users in the conversation
- **Confidence Score**: 0.0 to 1.0 based on detected patterns

## Error Handling

All endpoints include comprehensive error handling:
- Input validation
- Database connection errors
- Missing required fields
- Invalid data formats

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Testing Database Connection
```bash
python check_env.py
```

## Next Steps

- [ ] Email notification system
- [ ] Enhanced availability parsing
- [ ] Meeting confirmation flow
- [ ] Real-time WebSocket support
- [ ] User authentication
- [ ] Meeting reminders 