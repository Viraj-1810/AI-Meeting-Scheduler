import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from models import EmailNotification

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Check if email configuration is available
        self.email_enabled = bool(self.smtp_username and self.smtp_password)
        
        if not self.email_enabled:
            print("⚠️ Email service disabled - SMTP credentials not configured")
        else:
            print("✅ Email service initialized")
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        if not self.email_enabled:
            return False
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            print("✅ Email connection test successful")
            return True
        except Exception as e:
            print(f"❌ Email connection test failed: {e}")
            return False
    
    def send_meeting_confirmation(self, meeting_data: dict, participants: List[str]) -> bool:
        """Send meeting confirmation email to all participants"""
        if not self.email_enabled:
            print("⚠️ Email service disabled - skipping email send")
            return False
        
        try:
            # Create email content
            subject = f"Meeting Confirmed: {meeting_data.get('title', 'Team Meeting')}"
            
            # Format the meeting details
            meeting_date = meeting_data.get('date', 'TBD')
            meeting_time = meeting_data.get('time', 'TBD')
            meeting_title = meeting_data.get('title', 'Team Meeting')
            meeting_description = meeting_data.get('description', 'No description provided')
            
            # Create HTML email body
            html_body = self._create_meeting_confirmation_html(
                meeting_title, meeting_date, meeting_time, 
                meeting_description, participants
            )
            
            # Create plain text body
            text_body = self._create_meeting_confirmation_text(
                meeting_title, meeting_date, meeting_time, 
                meeting_description, participants
            )
            
            # Send to each participant
            success_count = 0
            for participant_email in participants:
                if self._send_email(participant_email, subject, text_body, html_body):
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
        if not self.email_enabled:
            return False
        
        try:
            subject = f"Meeting Reminder: {meeting_data.get('title', 'Team Meeting')}"
            
            meeting_date = meeting_data.get('date', 'TBD')
            meeting_time = meeting_data.get('time', 'TBD')
            meeting_title = meeting_data.get('title', 'Team Meeting')
            
            html_body = self._create_meeting_reminder_html(
                meeting_title, meeting_date, meeting_time, participants
            )
            
            text_body = self._create_meeting_reminder_text(
                meeting_title, meeting_date, meeting_time, participants
            )
            
            success_count = 0
            for participant_email in participants:
                if self._send_email(participant_email, subject, text_body, html_body):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending meeting reminder: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        """Send a single email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Attach both text and HTML versions
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return False
    
    def _create_meeting_confirmation_html(self, title: str, date: str, time: str, 
                                        description: str, participants: List[str]) -> str:
        """Create HTML email body for meeting confirmation"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Meeting Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .meeting-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Meeting Confirmed</h1>
                </div>
                <div class="content">
                    <h2>{title}</h2>
                    <div class="meeting-details">
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Time:</strong> {time}</p>
                        <p><strong>Description:</strong> {description}</p>
                        <p><strong>Participants:</strong> {', '.join(participants)}</p>
                    </div>
                    <p>Your meeting has been successfully scheduled. Please add this to your calendar.</p>
                    <p>If you need to make any changes, please contact the meeting organizer.</p>
                </div>
                <div class="footer">
                    <p>This email was sent by the Meeting Scheduler AI Assistant</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
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
    
    def _create_meeting_reminder_html(self, title: str, date: str, time: str, 
                                     participants: List[str]) -> str:
        """Create HTML email body for meeting reminder"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Meeting Reminder</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .meeting-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #FF9800; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Meeting Reminder</h1>
                </div>
                <div class="content">
                    <h2>{title}</h2>
                    <div class="meeting-details">
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Time:</strong> {time}</p>
                        <p><strong>Participants:</strong> {', '.join(participants)}</p>
                    </div>
                    <p>This is a reminder for your upcoming meeting. Please be prepared and join on time.</p>
                </div>
                <div class="footer">
                    <p>This email was sent by the Meeting Scheduler AI Assistant</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
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

# Global email service instance
email_service = None

def get_email_service() -> EmailService:
    """Get email service instance"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service 