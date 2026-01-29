# Invoice Generator SaaS

A complete, production-grade subscription-based invoice generator built with FastAPI, PostgreSQL, and Razorpay.

## Features

- **Subscription Model**: Free (3 invoices) and Paid (₹99/month unlimited)
- **GST Compliance**: Automatic CGST/SGST/IGST calculations
- **PDF Generation**: Professional A4 invoices with WeasyPrint
- **Customization**: Logo, stamps, company details, invoice templates
- **Payment Integration**: Razorpay subscriptions
- **Security**: JWT auth, bcrypt hashing, OWASP compliant

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Frontend**: HTML5, Bootstrap 5, Jinja2
- **Database**: PostgreSQL
- **PDF**: WeasyPrint
- **Payments**: Razorpay
- **Deployment**: Docker, Nginx, Gunicorn

## Quick Start

1. **Clone and setup**:
```bash
git clone <repo>
cd invoice-generator-saas
cp .env.example .env
# Edit .env with your credentials
```

2. **Deploy with Docker**:
```bash
docker compose up -d
```

3. **Access the application**:
- App: http://localhost
- Admin: http://localhost/admin

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://postgres:password@db:5432/invoicedb

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Development

1. **Setup virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run migrations**:
```bash
alembic upgrade head
```

4. **Start development server**:
```bash
uvicorn app.main:app --reload
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Deployment

The application is production-ready with:
- Multi-stage Docker builds
- Nginx reverse proxy
- Gunicorn WSGI server
- PostgreSQL database
- SSL/TLS support
- Security headers
- Rate limiting

## API Documentation

- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## License

MIT License