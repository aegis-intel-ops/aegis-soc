from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, osint, shodan, spiderfoot

app = FastAPI(
    title="Aegis OSINT API",
    description="Open Source Intelligence gathering service",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(osint.router, prefix="/api/osint", tags=["OSINT"])
app.include_router(shodan.router, prefix="/api/osint/shodan", tags=["Shodan"])
app.include_router(spiderfoot.router, prefix="/api/osint/spiderfoot", tags=["SpiderFoot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

