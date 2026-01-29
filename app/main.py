"""Main FastAPI application."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os

from app.config import settings
from app.database import create_tables
from app.api import auth, users, subscriptions, invoices, files, settings as settings_api, webhooks
from app.web.routes import router as web_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Professional Invoice Generator SaaS",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else list(settings.allowed_hosts)
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else list(settings.allowed_hosts),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# API routes
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

# Import new API routes
from app.api import notifications, audit, payment_receipts, templates

app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(payment_receipts.router, prefix="/api/receipts", tags=["payment-receipts"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

# Web routes
app.include_router(web_router)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    else:
        # For web routes, you might want to render an error page
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    if settings.debug:
        raise exc
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Create database tables
    create_tables()
    
    # Create default plans if they don't exist
    from app.database import SessionLocal
    from app.models.plan import Plan
    
    db = SessionLocal()
    try:
        # Check if plans exist
        existing_plans = db.query(Plan).count()
        
        if existing_plans == 0:
            # Create default plans
            free_plan = Plan(
                name="Free",
                description="Free plan with basic features",
                price=0,
                currency="INR",
                interval="monthly",
                invoice_limit=3,
                features='["Basic invoicing", "3 invoices per month", "Basic templates"]',
                is_active=True
            )
            
            pro_plan = Plan(
                name="Pro",
                description="Professional plan with all features",
                price=settings.paid_plan_price,
                currency="INR",
                interval="monthly",
                invoice_limit=None,  # Unlimited
                features='["Unlimited invoices", "PDF download", "Custom branding", "GST calculations", "Priority support"]',
                is_active=True,
                razorpay_plan_id="plan_pro_monthly"  # Set this to your actual Razorpay plan ID
            )
            
            db.add(free_plan)
            db.add(pro_plan)
            db.commit()
            
            print("Default plans created successfully")
        
    except Exception as e:
        print(f"Error creating default plans: {e}")
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}

# Root redirect
@app.get("/favicon.ico")
async def favicon():
    """Favicon redirect."""
    return JSONResponse(status_code=404, content={"detail": "Not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )