from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import health, clients, cases, alerts
from security import RateLimitMiddleware, LoggingMiddleware, verify_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title="Aegis SOC Core API",
    description="Security Operations Center - Client, Case, and Alert Management",
    version="1.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add security middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with optional API key dependency
app.include_router(health.router, tags=["Health"])
app.include_router(
    clients.router, 
    prefix="/api/soc/clients", 
    tags=["Clients"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    cases.router, 
    prefix="/api/soc/cases", 
    tags=["Cases"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    alerts.router, 
    prefix="/api/soc/alerts", 
    tags=["Alerts"],
    dependencies=[Depends(verify_api_key)]
)

@app.get("/")
async def root():
    return {
        "service": "Aegis SOC Core",
        "version": "1.1.0",
        "security": "API Key authentication (X-API-Key header)",
        "rate_limit": "100 requests per 60 seconds",
        "endpoints": {
            "clients": "/api/soc/clients",
            "cases": "/api/soc/cases",
            "alerts": "/api/soc/alerts",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)

