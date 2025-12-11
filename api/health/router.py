from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


@router.get("/health", status_code=200)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies the API and database are functioning properly.
    Returns a 200 status if everything is OK.
    """
    try:
        # Test database connectivity by running a simple query
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API and database are running normally"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "disconnected",
                "message": f"Database connection failed: {str(e)}"
            }
        )


@router.get("/ready", status_code=200)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint that indicates if the service is ready to accept traffic.
    This checks if the database is accessible.
    """
    try:
        # Test database connectivity
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "database": "available",
            "message": "Service is ready to accept requests"
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "database": "unavailable",
                "message": "Service is not ready to accept requests"
            }
        )