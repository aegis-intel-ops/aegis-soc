"""
Aegis API Security Middleware
- API Key Authentication
- Rate Limiting
- Request Logging
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import time
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aegis-api")

# API Key configuration
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
VALID_API_KEYS = set(os.getenv("API_KEYS", "aegis-dev-key,aegis-admin-key").split(","))
PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # window in seconds

# In-memory rate limit storage (use Redis in production)
rate_limit_store = defaultdict(list)

def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

async def verify_api_key(
    request: Request,
    api_key: str = Depends(API_KEY_HEADER)
) -> str:
    """Verify API key for protected endpoints"""
    # Skip auth for public paths
    if request.url.path in PUBLIC_PATHS:
        return "public"
    
    # Skip auth for docs paths
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
        return "public"
    
    # Check if auth is disabled (development mode)
    if os.getenv("DISABLE_AUTH", "false").lower() == "true":
        return "dev-mode"
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return api_key

def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_store[client_id] = [
        t for t in rate_limit_store[client_id] if t > window_start
    ]
    
    # Check limit
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Record request
    rate_limit_store[client_id].append(now)
    return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)
        
        # Skip rate limiting for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = get_client_ip(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"IP: {client_ip}"
        )
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error. Please try again later."
            )
