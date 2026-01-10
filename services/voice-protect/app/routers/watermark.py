from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import os

router = APIRouter()

class WatermarkResult(BaseModel):
    watermark_id: str
    original_filename: str
    watermarked_url: str
    verification_code: str

class VerifyResult(BaseModel):
    watermark_id: str
    is_valid: bool
    owner: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("/watermark", response_model=WatermarkResult)
async def add_watermark(
    audio: UploadFile = File(...),
    owner: Optional[str] = None
):
    """Add invisible watermark to audio file for ownership verification"""
    
    # Validate file type
    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate watermark ID
    watermark_id = str(uuid.uuid4())[:8].upper()
    
    # Save uploaded file
    upload_dir = "/app/data/uploads"
    output_dir = "/app/data/outputs"
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{watermark_id}_{audio.filename}"
    output_path = f"{output_dir}/{watermark_id}_watermarked.wav"
    
    with open(file_path, "wb") as f:
        content = await audio.read()
        f.write(content)
    
    # TODO: Integrate actual watermarking (librosa, pydub)
    # For now, just copy the file
    import shutil
    shutil.copy(file_path, output_path)
    
    return WatermarkResult(
        watermark_id=watermark_id,
        original_filename=audio.filename,
        watermarked_url=f"/api/voice/download/{watermark_id}",
        verification_code=f"AEGIS-{watermark_id}"
    )

@router.get("/verify/{watermark_id}", response_model=VerifyResult)
async def verify_watermark(watermark_id: str):
    """Verify if a watermark exists and retrieve ownership info"""
    
    # TODO: Lookup in database
    output_path = f"/app/data/outputs/{watermark_id}_watermarked.wav"
    
    if os.path.exists(output_path):
        return VerifyResult(
            watermark_id=watermark_id,
            is_valid=True,
            owner="Unknown",
            timestamp="2026-01-10"
        )
    
    return VerifyResult(
        watermark_id=watermark_id,
        is_valid=False
    )

@router.get("/download/{watermark_id}")
async def download_watermarked(watermark_id: str):
    """Download watermarked audio file"""
    from fastapi.responses import FileResponse
    
    output_path = f"/app/data/outputs/{watermark_id}_watermarked.wav"
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        output_path, 
        filename=f"watermarked_{watermark_id}.wav",
        media_type="audio/wav"
    )
