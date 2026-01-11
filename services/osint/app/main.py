from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import health, osint, shodan, spiderfoot
from security import RateLimitMiddleware, LoggingMiddleware, verify_api_key

app = FastAPI(
    title="Aegis OSINT API",
    description="Open Source Intelligence gathering service",
    version="2.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Security middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(osint.router, prefix="/api/osint", tags=["OSINT"], dependencies=[Depends(verify_api_key)])
app.include_router(shodan.router, prefix="/api/osint/shodan", tags=["Shodan"], dependencies=[Depends(verify_api_key)])
app.include_router(spiderfoot.router, prefix="/api/osint/spiderfoot", tags=["SpiderFoot"], dependencies=[Depends(verify_api_key)])

@app.get("/")
async def root():
    return {
        "service": "Aegis OSINT API",
        "version": "2.1.0",
        "security": "API Key auth (X-API-Key) - disabled in dev",
        "rate_limit": "100 requests per 60 seconds",
        "endpoints": {
            "osint": "/api/osint",
            "shodan": "/api/osint/shodan",
            "spiderfoot": "/api/osint/spiderfoot",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


