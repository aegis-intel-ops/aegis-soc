"""
API Security - Authentication, Rate Limiting, Logging
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aegis")

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
VALID_API_KEYS = set(os.getenv("API_KEYS", "aegis-dev-key,aegis-admin-key").split(","))
PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))
rate_store = defaultdict(list)

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")

async def verify_api_key(request: Request, api_key: str = Depends(API_KEY_HEADER)) -> str:
    if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/docs"):
        return "public"
    if os.getenv("DISABLE_AUTH", "true").lower() == "true":
        return "dev"
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        client = get_client_ip(request)
        now = time.time()
        rate_store[client] = [t for t in rate_store[client] if t > now - RATE_WINDOW]
        if len(rate_store[client]) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        rate_store[client].append(now)
        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {time.time()-start:.3f}s")
        return response
