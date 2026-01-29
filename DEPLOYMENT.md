# Invoice Generator SaaS - Deployment Guide

## 🚀 Complete Production-Ready Deployment

This guide will help you deploy the Invoice Generator SaaS application in a production environment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: Minimum 10GB free space
- **Network**: Internet connection for downloading dependencies

### Required Software
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

### Optional (for development)
- **Python**: 3.11+
- **PostgreSQL**: 15+ (if running without Docker)
- **Node.js**: 18+ (for frontend development)

## 🛠️ Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd invoice-generator-saas
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (IMPORTANT!)
nano .env  # or use your preferred editor
```

### 3. Update Environment Variables
Edit `.env` file with your actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/invoicedb

# Security Keys (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Razorpay Configuration (Required for payments)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Deploy with Docker (Recommended)
```bash
# Make deployment script executable (Linux/macOS)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 5. Manual Docker Deployment
If the script doesn't work, deploy manually:

```bash
# Create necessary directories
mkdir -p uploads/{logos,stamps,pdfs,documents}

# Start services
docker-compose up -d --build

# Wait for database to be ready (30-60 seconds)
docker-compose logs db

# Run database migrations
docker-compose exec app alembic upgrade head

# Check service status
docker-compose ps
```

## 🔧 Configuration Details

### Database Setup
The application uses PostgreSQL with the following default configuration:
- **Database**: `invoicedb`
- **User**: `postgres`
- **Port**: `5432`
- **Host**: `db` (Docker internal network)

### File Storage
- **Uploads**: `./uploads/` directory
- **Static Files**: `./static/` directory
- **PDF Generation**: Stored in `./uploads/pdfs/`

### Security Configuration
- **JWT Tokens**: 24-hour expiration by default
- **Password Hashing**: bcrypt with salt
- **File Upload**: 5MB limit, restricted file types
- **Rate Limiting**: Configured in Nginx

## 🌐 Accessing the Application

### Web Interface
- **Main Application**: http://localhost
- **API Documentation**: http://localhost/docs
- **Admin Interface**: http://localhost/admin

### Default Accounts
No default accounts are created. You need to:
1. Visit http://localhost/register
2. Create your first user account
3. The first user can be promoted to admin if needed

## 📊 Monitoring and Maintenance

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f nginx
```

### Service Management
```bash
# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update application
git pull
docker-compose up -d --build
```

### Database Management
```bash
# Access database
docker-compose exec db psql -U postgres -d invoicedb

# Backup database
docker-compose exec db pg_dump -U postgres invoicedb > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres invoicedb < backup.sql
```

### File Backups
```bash
# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Restore uploads
tar -xzf uploads-backup.tar.gz
```

## 🔒 Production Security

### SSL/TLS Setup
For production, configure SSL certificates:

1. **Update nginx.conf** with SSL configuration
2. **Obtain certificates** (Let's Encrypt recommended)
3. **Update docker-compose.yml** to mount certificates

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 22/tcp    # SSH (if needed)
ufw enable
```

### Security Headers
The application includes security headers:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Content Security Policy

## 📈 Performance Optimization

### Database Optimization
- Regular VACUUM and ANALYZE
- Monitor query performance
- Set up connection pooling if needed

### Application Scaling
- Increase Gunicorn workers: Edit `docker-compose.yml`
- Add Redis for caching (optional)
- Set up load balancer for multiple instances

### File Storage
- Consider cloud storage (AWS S3, Google Cloud) for uploads
- Implement CDN for static files
- Regular cleanup of old PDF files

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose logs app

# Common solutions
docker-compose down
docker-compose up -d --build
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER uploads/
chmod -R 755 uploads/
```

#### Memory Issues
```bash
# Check resource usage
docker stats

# Increase Docker memory limits if needed
```

### Health Checks
```bash
# Application health
curl http://localhost/health

# Database health
docker-compose exec db pg_isready -U postgres

# Service status
docker-compose ps
```

## 🔄 Updates and Maintenance

### Regular Updates
```bash
# Update application code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run any new migrations
docker-compose exec app alembic upgrade head
```

### Database Migrations
```bash
# Check current migration status
docker-compose exec app alembic current

# Run pending migrations
docker-compose exec app alembic upgrade head

# Rollback if needed
docker-compose exec app alembic downgrade -1
```

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and code comments
- **Logs**: Always check application logs first
- **Issues**: Create GitHub issues for bugs
- **Community**: Join our community discussions

### Reporting Issues
When reporting issues, include:
1. Error messages from logs
2. Steps to reproduce
3. Environment details
4. Configuration (without sensitive data)

## 🎯 Production Checklist

Before going live, ensure:

- [ ] Environment variables are properly configured
- [ ] Database backups are set up
- [ ] SSL certificates are installed
- [ ] Firewall rules are configured
- [ ] Monitoring is in place
- [ ] Error tracking is configured
- [ ] Performance testing is completed
- [ ] Security audit is performed
- [ ] Documentation is updated
- [ ] Team is trained on maintenance procedures

## 📝 License and Legal

- Review Terms of Service and Privacy Policy
- Ensure compliance with local regulations
- Set up proper data retention policies
- Configure GDPR compliance if applicable

---

**🎉 Congratulations!** Your Invoice Generator SaaS is now ready for production use.

For additional support or questions, please refer to the documentation or contact the development team.