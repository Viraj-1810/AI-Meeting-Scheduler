from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from bson import ObjectId

# Pydantic models for API requests/responses
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    name: str
    email: str
    message: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    date: str
    time: str
    participants: List[str]
    title: Optional[str] = None
    description: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: str
    created_at: datetime
    status: str = "scheduled"  # scheduled, cancelled, completed
    
    class Config:
        from_attributes = True

class MeetingIntent(BaseModel):
    intent_detected: bool
    confidence: float
    extracted_dates: List[str] = []
    extracted_times: List[str] = []
    participants: List[str] = []
    suggested_date: Optional[str] = None
    suggested_time: Optional[str] = None
    missing_info: List[str] = []

class EmailNotification(BaseModel):
    to_emails: List[str]
    subject: str
    body: str
    meeting_id: str
