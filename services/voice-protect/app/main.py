from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, analyze, watermark

app = FastAPI(
    title="Aegis Voice Protection API",
    description="AI audio detection and watermarking service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router, prefix="/api/voice", tags=["Analysis"])
app.include_router(watermark.router, prefix="/api/voice", tags=["Watermark"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
