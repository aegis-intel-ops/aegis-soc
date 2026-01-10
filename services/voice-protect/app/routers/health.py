from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "voice-protect",
        "version": "1.0.0"
    }
