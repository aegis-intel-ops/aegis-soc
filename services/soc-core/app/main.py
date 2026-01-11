from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import health, clients, cases, alerts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title="Aegis SOC Core API",
    description="Security Operations Center - Client, Case, and Alert Management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(clients.router, prefix="/api/soc/clients", tags=["Clients"])
app.include_router(cases.router, prefix="/api/soc/cases", tags=["Cases"])
app.include_router(alerts.router, prefix="/api/soc/alerts", tags=["Alerts"])

@app.get("/")
async def root():
    return {
        "service": "Aegis SOC Core",
        "version": "1.0.0",
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
