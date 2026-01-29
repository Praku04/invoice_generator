# Email Configuration Options

## Option 1: Mailtrap (Testing - Recommended)
Perfect for development and testing. Emails are captured but not actually sent.

```env
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your-mailtrap-username
SMTP_PASSWORD=your-mailtrap-password
FROM_EMAIL=noreply@invoicegen.com
```

Setup:
1. Go to https://mailtrap.io/
2. Sign up for free
3. Create an inbox
4. Get SMTP credentials from inbox settings

## Option 2: SendGrid (Production)
Free tier: 100 emails/day

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=your-verified-email@yourdomain.com
```

Setup:
1. Go to https://sendgrid.com/
2. Sign up for free account
3. Create API key in Settings → API Keys
4. Verify sender email in Settings → Sender Authentication

## Option 3: Mailgun (Production)
Free tier: 5,000 emails/month for 3 months

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
FROM_EMAIL=noreply@your-domain.mailgun.org
```

Setup:
1. Go to https://www.mailgun.com/
2. Sign up for free account
3. Add and verify domain
4. Get SMTP credentials from domain settings

## Option 4: Outlook/Hotmail (Personal)
If you have Outlook/Hotmail account:

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-outlook-password
FROM_EMAIL=your-email@outlook.com
```

Note: May require enabling "Less secure app access" in account settings.

## Option 5: Yahoo Mail (Personal)
If you have Yahoo account:

```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-yahoo-app-password
FROM_EMAIL=your-email@yahoo.com
```

Note: Requires generating app password in Yahoo account security settings.

## Recommendation

For **testing/development**: Use Mailtrap
For **production**: Use SendGrid or Mailgun

Mailtrap is the easiest to set up and perfect for testing your email functionality without actually sending emails to real users.