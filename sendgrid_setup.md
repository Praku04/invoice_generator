# SendGrid Free Setup (100 emails/day)

## Configuration for .env:
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key-here
FROM_EMAIL=your-verified-email@gmail.com
```

## Setup Steps:
1. Go to https://sendgrid.com/free/
2. Sign up for free account (no credit card required)
3. Verify your email address
4. Go to Settings → API Keys
5. Click "Create API Key"
6. Choose "Restricted Access" 
7. Give it "Mail Send" permissions
8. Copy the API key (starts with SG.)
9. Use "apikey" as username and the API key as password

## Email Verification:
- Go to Settings → Sender Authentication
- Click "Verify a Single Sender"
- Enter your email address (can be Gmail, Yahoo, etc.)
- Verify the email they send you

## Limits:
- 100 emails per day (FREE forever)
- Perfect for small applications