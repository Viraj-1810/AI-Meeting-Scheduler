import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DemoEmailService:
    """Demo email service that simulates email sending for testing"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Check if real email configuration is available
        self.real_email_enabled = bool(self.smtp_username and self.smtp_password)
        
        if self.real_email_enabled:
            print("✅ Real email service available - will send actual emails")
        else:
            print("🔄 Demo email service enabled - emails will be simulated")
        
        # Demo mode is always enabled for testing
        self.email_enabled = True
    
    def test_connection(self) -> bool:
        """Test email connection (simulated in demo mode)"""
        if self.real_email_enabled:
            # Test real SMTP connection
            try:
                import smtplib
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.quit()
                print("✅ Real email connection test successful")
                return True
            except Exception as e:
                print(f"❌ Real email connection test failed: {e}")
                return False
        else:
            # Simulate successful connection
            print("✅ Demo email connection test successful (simulated)")
            return True
    
    def send_meeting_confirmation(self, meeting_data: dict, participants: List[str]) -> bool:
        """Send meeting confirmation email to all participants"""
        try:
            # Create email content
            subject = f"Meeting Confirmed: {meeting_data.get('title', 'Team Meeting')}"
            
            # Format the meeting details
            meeting_date = meeting_data.get('date', 'TBD')
            meeting_time = meeting_data.get('time', 'TBD')
            meeting_title = meeting_data.get('title', 'Team Meeting')
            meeting_description = meeting_data.get('description', 'No description provided')
            
            # Create email body
            email_body = self._create_meeting_confirmation_text(
                meeting_title, meeting_date, meeting_time, 
                meeting_description, participants
            )
            
            # Send to each participant
            success_count = 0
            for participant_email in participants:
                if self._send_email(participant_email, subject, email_body):
                    success_count += 1
                    print(f"✅ Confirmation email sent to {participant_email}")
                else:
                    print(f"❌ Failed to send email to {participant_email}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending meeting confirmation: {e}")
            return False
    
    def send_meeting_reminder(self, meeting_data: dict, participants: List[str]) -> bool:
        """Send meeting reminder email"""
        try:
            subject = f"Meeting Reminder: {meeting_data.get('title', 'Team Meeting')}"
            
            meeting_date = meeting_data.get('date', 'TBD')
            meeting_time = meeting_data.get('time', 'TBD')
            meeting_title = meeting_data.get('title', 'Team Meeting')
            
            email_body = self._create_meeting_reminder_text(
                meeting_title, meeting_date, meeting_time, participants
            )
            
            success_count = 0
            for participant_email in participants:
                if self._send_email(participant_email, subject, email_body):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending meeting reminder: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send a single email (simulated in demo mode)"""
        try:
            if self.real_email_enabled:
                # Send real email
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.smtp_username
                msg['To'] = to_email
                
                text_part = MIMEText(body, 'plain')
                msg.attach(text_part)
                
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                
                return True
            else:
                # Simulate email sending
                print(f"📧 [DEMO] Email would be sent to: {to_email}")
                print(f"📧 [DEMO] Subject: {subject}")
                print(f"📧 [DEMO] Body: {body[:100]}...")
                print("📧 [DEMO] Email simulation successful")
                return True
                
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return False
    
    def _create_meeting_confirmation_text(self, title: str, date: str, time: str, 
                                        description: str, participants: List[str]) -> str:
        """Create plain text email body for meeting confirmation"""
        return f"""
Meeting Confirmation

Title: {title}
Date: {date}
Time: {time}
Description: {description}
Participants: {', '.join(participants)}

Your meeting has been successfully scheduled. Please add this to your calendar.

If you need to make any changes, please contact the meeting organizer.

---
Generated by Meeting Scheduler AI Assistant
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def _create_meeting_reminder_text(self, title: str, date: str, time: str, 
                                     participants: List[str]) -> str:
        """Create plain text email body for meeting reminder"""
        return f"""
Meeting Reminder

Title: {title}
Date: {date}
Time: {time}
Participants: {', '.join(participants)}

This is a reminder for your upcoming meeting. Please be prepared and join on time.

---
Generated by Meeting Scheduler AI Assistant
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

# Global demo email service instance
demo_email_service = None

def get_demo_email_service() -> DemoEmailService:
    """Get demo email service instance"""
    global demo_email_service
    if demo_email_service is None:
        demo_email_service = DemoEmailService()
    return demo_email_service 