#!/bin/bash

# Invoice Generator SaaS Deployment Script
# This script sets up and deploys the complete application

set -e  # Exit on any error

echo "🚀 Starting Invoice Generator SaaS Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads/logos
    mkdir -p uploads/stamps  
    mkdir -p uploads/pdfs
    mkdir -p uploads/documents
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p static/images
    
    print_success "Directories created"
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "Please update .env with your actual configuration values:"
        print_warning "- Database credentials"
        print_warning "- JWT secret keys"
        print_warning "- Razorpay API keys"
        print_warning "- SMTP settings (optional)"
    else
        print_success "Environment file already exists"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Services started successfully"
}

# Wait for database to be ready
wait_for_database() {
    print_status "Waiting for database to be ready..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Database not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Database failed to start within expected time"
    exit 1
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait a bit more to ensure app container is ready
    sleep 5
    
    docker-compose exec app alembic upgrade head
    
    print_success "Database migrations completed"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to be fully ready
    sleep 10
    
    # Check if app is responding
    if curl -f http://localhost/health >/dev/null 2>&1; then
        print_success "Application is healthy and responding"
    else
        print_warning "Application health check failed, but services may still be starting..."
    fi
    
    # Show service status
    docker-compose ps
}

# Display deployment information
show_deployment_info() {
    print_success "🎉 Deployment completed successfully!"
    echo
    echo "📋 Deployment Information:"
    echo "=========================="
    echo "🌐 Application URL: http://localhost"
    echo "📊 Admin Panel: http://localhost/admin (create admin user first)"
    echo "📖 API Documentation: http://localhost/docs"
    echo "🗄️  Database: PostgreSQL on localhost:5432"
    echo
    echo "📁 Important Directories:"
    echo "- Uploads: ./uploads/"
    echo "- Static files: ./static/"
    echo "- Logs: Use 'docker-compose logs' to view"
    echo
    echo "🔧 Management Commands:"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo "- Restart services: docker-compose restart"
    echo "- Update application: git pull && docker-compose up -d --build"
    echo
    echo "⚙️  Configuration:"
    echo "- Environment: .env file"
    echo "- Database migrations: docker-compose exec app alembic upgrade head"
    echo "- Create admin user: Use the web interface at /register"
    echo
    print_warning "🔐 Security Reminders:"
    echo "- Update default passwords in .env file"
    echo "- Configure proper JWT secrets"
    echo "- Set up SSL/TLS for production"
    echo "- Configure firewall rules"
    echo "- Set up regular backups"
    echo
    print_success "✅ Your Invoice Generator SaaS is ready to use!"
}

# Main deployment process
main() {
    echo "Invoice Generator SaaS - Production Deployment"
    echo "=============================================="
    echo
    
    check_docker
    create_directories
    setup_environment
    start_services
    wait_for_database
    run_migrations
    check_health
    show_deployment_info
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main

exit 0