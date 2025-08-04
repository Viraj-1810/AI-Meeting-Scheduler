# Email Setup Guide

## Current Status
The meeting scheduler now has **email functionality working in demo mode**. When you schedule a meeting, the system will simulate sending confirmation emails to all participants.

## Demo Mode (Default)
- ✅ **Works out of the box** - No configuration needed
- ✅ **Simulates email sending** - Shows what emails would be sent
- ✅ **Perfect for testing** - See email content in console logs
- ✅ **No SMTP credentials required**

## Real Email Setup (Optional)

To enable real email sending, follow these steps:

### 1. Create .env file
Copy the template and create a `.env` file in the backend directory:

```bash
cp env_template.txt .env
```

### 2. Configure Gmail (Recommended)

#### Option A: Gmail App Password (Recommended)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Update your `.env` file:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
```

#### Option B: Other Email Providers
Update your `.env` file with your provider's settings:
```
SMTP_SERVER=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-email@your-provider.com
SMTP_PASSWORD=your-password
```

### 3. Test Email Configuration
Restart the backend server and test the email functionality:
```bash
python app.py
```

Then use the "Test Email" feature in the frontend or call:
```bash
curl -X POST http://localhost:5000/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Email Features

### Meeting Confirmations
- ✅ **Automatic sending** when meetings are scheduled
- ✅ **HTML and text versions** for compatibility
- ✅ **Professional templates** with meeting details
- ✅ **All participants** receive confirmations

### Email Content
- Meeting title, date, and time
- Participant list
- Meeting description
- Professional formatting
- Generated timestamp

## Troubleshooting

### Demo Mode Issues
- Check console logs for email simulation messages
- Verify participants have valid email addresses
- Ensure meeting scheduling is successful

### Real Email Issues
- Verify SMTP credentials in `.env` file
- Check Gmail App Password is correct
- Ensure 2-factor authentication is enabled
- Test connection with `/test-email` endpoint

### Common Error Messages
- `"Email service disabled"` → Using demo mode (normal)
- `"SMTP credentials not configured"` → Need to set up `.env` file
- `"Email connection test failed"` → Check SMTP settings

## Security Notes
- Never commit your `.env` file to version control
- Use App Passwords instead of regular passwords
- Keep SMTP credentials secure
- Consider using environment variables in production

## Production Deployment
For production use, consider:
- Using a dedicated email service (SendGrid, Mailgun, etc.)
- Setting up proper DNS records
- Implementing email rate limiting
- Adding email templates and branding 