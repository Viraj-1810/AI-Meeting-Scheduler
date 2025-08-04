import re
import dateparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models import MeetingIntent

def analyze_meeting_intent(message: str) -> MeetingIntent:
    """
    Simplified meeting intent detection using regex and dateparser
    """
    message_lower = message.lower()
    
    # Check for meeting-related keywords (more flexible)
    meeting_keywords = [
        'meeting', 'schedule', 'appointment', 'call', 'discussion',
        'sync', 'catch up', 'get together', 'meet up', 'meet',
        'book', 'arrange', 'set up', 'organize', 'plan',
        'conference', 'video call', 'zoom', 'teams', 'google meet',
        'hangout', 'coffee', 'lunch', 'dinner', 'breakfast',
        'standup', 'stand up', 'daily', 'weekly', 'monthly',
        'review', 'brainstorm', 'workshop', 'training', 'presentation'
    ]
    
    # More flexible intent detection
    intent_detected = any(keyword in message_lower for keyword in meeting_keywords)
    
    # Also check for time-related words that suggest scheduling
    time_words = ['when', 'what time', 'available', 'free', 'busy', 'can', 'could']
    if any(word in message_lower for word in time_words):
        intent_detected = True
    
    if not intent_detected:
        return MeetingIntent(
            intent_detected=False,
            confidence=0.0,
            extracted_dates=[],
            extracted_times=[],
            participants=[],
            suggested_date=None,
            suggested_time=None,
            missing_info=[]
        )
    
    # Extract dates (more flexible patterns)
    date_patterns = [
        # Relative dates
        r'tomorrow',
        r'today',
        r'yesterday',
        r'next week',
        r'this week',
        r'last week',
        r'next month',
        r'this month',
        r'next year',
        r'this year',
        
        # Days of week
        r'next monday', r'next tuesday', r'next wednesday', r'next thursday', 
        r'next friday', r'next saturday', r'next sunday',
        r'this monday', r'this tuesday', r'this wednesday', r'this thursday',
        r'this friday', r'this saturday', r'this sunday',
        r'monday', r'tuesday', r'wednesday', r'thursday', r'friday', r'saturday', r'sunday',
        
        # Specific dates
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{1,2}-\d{1,2}-\d{4}',
        r'\d{1,2}\.\d{1,2}\.\d{4}',
        r'\d{1,2}/\d{1,2}',
        r'\d{1,2}-\d{1,2}',
        
        # Month names
        r'january \d{1,2}', r'february \d{1,2}', r'march \d{1,2}', r'april \d{1,2}',
        r'may \d{1,2}', r'june \d{1,2}', r'july \d{1,2}', r'august \d{1,2}',
        r'september \d{1,2}', r'october \d{1,2}', r'november \d{1,2}', r'december \d{1,2}',
        
        # Flexible date expressions
        r'in \d+ days?',
        r'in \d+ weeks?',
        r'in \d+ months?',
        r'\d+ days? from now',
        r'\d+ weeks? from now',
        r'\d+ months? from now'
    ]
    
    extracted_dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, message_lower)
        for match in matches:
            try:
                parsed_date = dateparser.parse(match)
                if parsed_date:
                    extracted_dates.append(parsed_date.strftime('%Y-%m-%d'))
            except:
                continue
    
    # Extract times (more flexible patterns for natural language)
    time_patterns = [
        # Specific times with various formats
        r'\d{1,2}:\d{2}\s*(am|pm)',
        r'\d{1,2}\s*(am|pm)',
        r'\d{1,2}:\d{2}',
        r'\d{1,2}:\d{2}\s*(am|pm)',
        
        # Natural time expressions
        r'at \d{1,2}',
        r'around \d{1,2}',
        r'about \d{1,2}',
        r'\d{1,2}ish',
        r'\d{1,2} o\'clock',
        r'\d{1,2} o clock',
        r'\d{1,2} pm',
        r'\d{1,2} am',
        r'\d{1,2} PM',
        r'\d{1,2} AM',
        
        # Time periods
        r'morning',
        r'afternoon',
        r'evening',
        r'night',
        r'noon',
        r'midnight',
        r'early morning',
        r'late afternoon',
        r'late evening',
        
        # Business hours
        r'business hours',
        r'office hours',
        r'work hours',
        r'9 to 5',
        r'9-5',
        
        # Common natural expressions
        r'this afternoon',
        r'this morning',
        r'this evening',
        r'tomorrow morning',
        r'tomorrow afternoon',
        r'tomorrow evening',
        r'next morning',
        r'next afternoon',
        r'next evening'
    ]
    
    extracted_times = []
    for pattern in time_patterns:
        matches = re.findall(pattern, message_lower)
        for match in matches:
            if isinstance(match, tuple):
                match = ''.join(match)
            
            # Convert natural language to specific times
            if match in ['morning', 'this morning', 'tomorrow morning', 'next morning']:
                extracted_times.append("9:00 AM")
            elif match in ['afternoon', 'this afternoon', 'tomorrow afternoon', 'next afternoon']:
                extracted_times.append("2:00 PM")
            elif match in ['evening', 'this evening', 'tomorrow evening', 'next evening']:
                extracted_times.append("6:00 PM")
            elif match in ['night', 'late evening']:
                extracted_times.append("8:00 PM")
            elif match == 'noon':
                extracted_times.append("12:00 PM")
            elif match == 'midnight':
                extracted_times.append("12:00 AM")
            elif match in ['business hours', 'office hours', 'work hours', '9 to 5', '9-5']:
                extracted_times.append("10:00 AM")
            else:
                # Handle specific time formats
                if 'am' in match.lower() or 'pm' in match.lower():
                    # Extract hour and format properly
                    hour_match = re.search(r'(\d{1,2})', match)
                    if hour_match:
                        hour = int(hour_match.group(1))
                        if 'pm' in match.lower() and hour != 12:
                            hour += 12
                        elif 'am' in match.lower() and hour == 12:
                            hour = 0
                        
                        # Format as 12-hour time
                        if hour == 0:
                            formatted_time = "12:00 AM"
                        elif hour < 12:
                            formatted_time = f"{hour}:00 AM"
                        elif hour == 12:
                            formatted_time = "12:00 PM"
                        else:
                            formatted_time = f"{hour-12}:00 PM"
                        
                        extracted_times.append(formatted_time)
                else:
                    # Handle times without AM/PM - use business context
                    hour_match = re.search(r'(\d{1,2})', match)
                    if hour_match:
                        hour = int(hour_match.group(1))
                        
                        # Business context: Most meetings are during business hours
                        # 5-12 without AM/PM is typically PM (afternoon/evening)
                        # 1-4 without AM/PM is typically PM (afternoon)
                        # 6-11 without AM/PM is typically AM (morning)
                        if hour >= 5 and hour <= 12:
                            formatted_time = f"{hour}:00 PM"
                        elif hour >= 1 and hour <= 4:
                            formatted_time = f"{hour}:00 PM"
                        elif hour >= 6 and hour <= 11:
                            formatted_time = f"{hour}:00 AM"
                        elif hour == 12:
                            formatted_time = "12:00 PM"
                        else:
                            # Default to PM for business hours
                            formatted_time = f"{hour}:00 PM"
                        
                        extracted_times.append(formatted_time)
                    else:
                        extracted_times.append(match)
    
    # Extract participants (more flexible name extraction)
    name_patterns = [
        # Direct mentions
        r'with\s+([a-zA-Z]+)',
        r'meet\s+([a-zA-Z]+)',
        r'([a-zA-Z]+)\s+and\s+([a-zA-Z]+)',
        r'([a-zA-Z]+),\s+([a-zA-Z]+)',
        r'([a-zA-Z]+)\s*&\s*([a-zA-Z]+)',
        
        # Team mentions
        r'team',
        r'everyone',
        r'all',
        r'group',
        r'us',
        r'we',
        
        # Role-based mentions
        r'manager',
        r'lead',
        r'developer',
        r'designer',
        r'stakeholder',
        r'client',
        r'customer'
    ]
    
    participants = []
    
    # Extract names from regex patterns
    for pattern in name_patterns:
        matches = re.findall(pattern, message_lower)
        for match in matches:
            if isinstance(match, tuple):
                participants.extend([name.capitalize() for name in match])
            else:
                participants.append(match.capitalize())
    
    # Extract participants from chat history (emails)
    # This will be handled by the extract_meeting_details function in app.py
    
    # Remove duplicates and filter out common words
    common_words = ['team', 'everyone', 'all', 'group', 'us', 'we', 'manager', 'lead', 'developer', 'designer', 'stakeholder', 'client', 'customer']
    participants = [p for p in participants if p.lower() not in common_words]
    participants = list(set(participants))
    
    # Determine missing information
    missing_info = []
    if not extracted_dates:
        missing_info.append("date")
    if not extracted_times:
        missing_info.append("time")
    if not participants:
        missing_info.append("participants")
    
    # Calculate confidence based on extracted information
    confidence = 0.3  # Base confidence for meeting intent
    if extracted_dates:
        confidence += 0.3
    if extracted_times:
        confidence += 0.2
    if participants:
        confidence += 0.2
    
    # Set suggested date and time from extracted data
    suggested_date = extracted_dates[0] if extracted_dates else None
    suggested_time = extracted_times[0] if extracted_times else None
    
    # If still no time, set a default time for the meeting
    if not suggested_time and suggested_date:
        suggested_time = "2:00 PM"  # Default to afternoon
    
    # If no time extracted, try to extract from common patterns
    if not suggested_time:
        # Look for time patterns in the original message
        time_keywords = ['am', 'pm', 'morning', 'afternoon', 'evening', 'noon', 'midnight', 'at', 'around', 'about']
        for keyword in time_keywords:
            if keyword in message_lower:
                if keyword == 'am' or keyword == 'pm':
                    # Look for hour before am/pm
                    hour_match = re.search(r'(\d{1,2})\s*(am|pm)', message_lower)
                    if hour_match:
                        hour = hour_match.group(1)
                        ampm = hour_match.group(2)
                        suggested_time = f"{hour}:00 {ampm.upper()}"
                        break
                elif keyword == 'at':
                    # Look for "at 2" or "at 2pm" patterns
                    at_match = re.search(r'at\s+(\d{1,2})(?:\s*(am|pm))?', message_lower)
                    if at_match:
                        hour = at_match.group(1)
                        ampm = at_match.group(2) if at_match.group(2) else 'pm'
                        suggested_time = f"{hour}:00 {ampm.upper()}"
                        break
                elif keyword in ['morning', 'afternoon', 'evening']:
                    if keyword == 'morning':
                        suggested_time = "9:00 AM"
                    elif keyword == 'afternoon':
                        suggested_time = "2:00 PM"
                    elif keyword == 'evening':
                        suggested_time = "6:00 PM"
                    break
                elif keyword == 'noon':
                    suggested_time = "12:00 PM"
                    break
                elif keyword == 'midnight':
                    suggested_time = "12:00 AM"
                    break
                elif keyword in ['around', 'about']:
                    # Look for "around 2" or "about 3" patterns
                    around_match = re.search(r'(around|about)\s+(\d{1,2})', message_lower)
                    if around_match:
                        hour = around_match.group(2)
                        suggested_time = f"{hour}:00 PM"
                        break
    
    return MeetingIntent(
        intent_detected=True,
        confidence=min(confidence, 1.0),
        extracted_dates=extracted_dates,
        extracted_times=extracted_times,
        participants=participants,
        suggested_date=suggested_date,
        suggested_time=suggested_time,
        missing_info=missing_info
    )

def suggest_meeting_times(participants: List[str], duration_minutes: int = 60) -> List[Dict[str, Any]]:
    """
    Suggest meeting times based on common availability
    """
    # Simple suggestion logic - in a real app, this would check calendars
    base_time = datetime.now()
    suggestions = []
    
    # Suggest times for the next 3 days
    for day_offset in range(1, 4):
        for hour in [9, 10, 11, 14, 15, 16]:  # Common business hours
            suggested_time = base_time + timedelta(days=day_offset)
            suggested_time = suggested_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            suggestions.append({
                "datetime": suggested_time.isoformat(),
                "date": suggested_time.strftime('%Y-%m-%d'),
                "time": suggested_time.strftime('%I:%M %p'),
                "duration_minutes": duration_minutes,
                "participants": participants
            })
    
    return suggestions[:6]  # Return top 6 suggestions 