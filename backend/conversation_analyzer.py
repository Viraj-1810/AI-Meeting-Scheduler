import re
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class ConversationAnalyzer:
    """Analyzes conversations to detect separate meeting contexts"""
    
    def __init__(self):
        self.time_window_minutes = 30  # Messages within this window are considered related
        self.participant_threshold = 2  # Minimum participants for a meeting
    
    def group_conversations(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group messages into separate conversation contexts
        """
        if not messages:
            return []
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', ''))
        
        conversation_groups = []
        current_group = []
        
        for i, message in enumerate(sorted_messages):
            if not current_group:
                current_group.append(message)
                continue
            
            # Check if this message belongs to current group
            if self._is_related_message(message, current_group):
                current_group.append(message)
            else:
                # Start new group - be more strict about participant separation
                if len(current_group) >= 1:  # Allow single message groups for better separation
                    conversation_groups.append(current_group)
                current_group = [message]
        
        # Add the last group
        if len(current_group) >= 1:
            conversation_groups.append(current_group)
        
        return conversation_groups
    
    def _is_related_message(self, message: Dict[str, Any], group: List[Dict[str, Any]]) -> bool:
        """
        Determine if a message is related to the current conversation group
        """
        if not group:
            return True
        
        # Check time proximity (shorter window for better separation)
        current_time = self._parse_timestamp(message.get('timestamp', ''))
        group_times = [self._parse_timestamp(msg.get('timestamp', '')) for msg in group]
        
        if current_time and group_times:
            time_diff = abs((current_time - min(group_times)).total_seconds() / 60)
            if time_diff > 15:  # Reduced from 30 to 15 minutes for stricter separation
                return False
        
        # Check participant overlap - this is the key for separating conversations
        group_participants = set(msg.get('email', '') for msg in group)
        current_participant = message.get('email', '')
        
        # If current participant is NOT in the group, start a new conversation
        if current_participant not in group_participants:
            return False
        
        # Check for conversation continuity keywords
        continuity_keywords = ['meeting', 'schedule', 'available', 'time', 'when', 'how about', 'works for me', 'ok', 'sure', 'yes', 'no']
        message_text = message.get('message', '').lower()
        group_text = ' '.join([msg.get('message', '').lower() for msg in group])
        
        # If current message contains meeting-related keywords, likely related
        if any(keyword in message_text for keyword in continuity_keywords):
            return True
        
        # If group contains meeting-related keywords, likely related
        if any(keyword in group_text for keyword in continuity_keywords):
            return True
        
        return False
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            if isinstance(timestamp_str, str):
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif isinstance(timestamp_str, datetime):
                return timestamp_str
            else:
                return datetime.now()
        except:
            return datetime.now()
    
    def extract_meeting_contexts(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract separate meeting contexts from conversation groups
        """
        conversation_groups = self.group_conversations(messages)
        meeting_contexts = []
        
        for group in conversation_groups:
            context = self._analyze_group_context(group)
            if context and context.get('participants'):
                meeting_contexts.append(context)
        
        return meeting_contexts
    
    def _analyze_group_context(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a conversation group to extract meeting context
        """
        participants = list(set(msg.get('email', '') for msg in group))
        messages_text = ' '.join([msg.get('message', '') for msg in group])
        
        # Extract time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2})',
            r'around\s+(\d{1,2})',
            r'(\d{1,2})\s*o\'?clock'
        ]
        
        extracted_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, messages_text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 3:  # hour:minute am/pm
                        hour, minute, ampm = match
                        time_str = f"{hour}:{minute} {ampm.upper()}"
                    elif len(match) == 2:  # hour am/pm
                        hour, ampm = match
                        time_str = f"{hour}:00 {ampm.upper()}"
                    else:
                        hour = int(match[0])
                        # Business context: Most meetings are during business hours
                        # 5-12 without AM/PM is typically PM (afternoon/evening)
                        # 1-4 without AM/PM is typically PM (afternoon)
                        # 6-11 without AM/PM is typically AM (morning)
                        if hour >= 5 and hour <= 12:
                            time_str = f"{hour}:00 PM"
                        elif hour >= 1 and hour <= 4:
                            time_str = f"{hour}:00 PM"
                        elif hour >= 6 and hour <= 11:
                            time_str = f"{hour}:00 AM"
                        elif hour == 12:
                            time_str = "12:00 PM"
                        else:
                            # Default to PM for business hours
                            time_str = f"{hour}:00 PM"
                    extracted_times.append(time_str)
        
        # Extract date patterns
        date_patterns = [
            r'tomorrow',
            r'today',
            r'friday',
            r'monday',
            r'next week'
        ]
        
        extracted_dates = []
        for pattern in date_patterns:
            if re.search(pattern, messages_text.lower()):
                extracted_dates.append(pattern)
        
        # Determine meeting intent - be more flexible
        meeting_keywords = ['meeting', 'schedule', 'call', 'discussion', 'standup', 'review', 'available', 'time', 'when']
        has_meeting_intent = any(keyword in messages_text.lower() for keyword in meeting_keywords)
        
        # Also check if there are time mentions (suggests scheduling)
        time_mentions = ['at', 'around', 'about', 'am', 'pm', 'morning', 'afternoon', 'evening']
        has_time_mention = any(time_word in messages_text.lower() for time_word in time_mentions)
        
        # If we have participants and either meeting intent or time mentions, create context
        if participants and (has_meeting_intent or has_time_mention):
            return {
                'participants': participants,
                'messages': group,
                'extracted_times': extracted_times,
                'extracted_dates': extracted_dates,
                'context_text': messages_text[:200] + '...' if len(messages_text) > 200 else messages_text,
                'message_count': len(group)
            }
        
        return None

def get_conversation_analyzer() -> ConversationAnalyzer:
    """Get conversation analyzer instance"""
    return ConversationAnalyzer() 