from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import os

router = APIRouter()

# In-memory job storage (use Redis in production)
jobs = {}

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    result_url: Optional[str] = None
    error: Optional[str] = None

@router.post("/fawkes")
async def fawkes_protect(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...)
):
    """Apply Fawkes face cloaking to protect image from facial recognition"""
    
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "result_url": None, "error": None}
    
    # Save uploaded file
    upload_dir = "/app/data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{job_id}_{image.filename}"
    
    with open(file_path, "wb") as f:
        content = await image.read()
        f.write(content)
    
    # Add processing to background
    background_tasks.add_task(process_fawkes, job_id, file_path)
    
    return {"job_id": job_id, "status": "pending"}

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """Get status of a protection job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        result_url=job.get("result_url"),
        error=job.get("error")
    )

async def process_fawkes(job_id: str, file_path: str):
    """Background task to run Fawkes protection"""
    try:
        jobs[job_id]["status"] = "processing"
        
        # TODO: Integrate actual Fawkes processing
        # from services.fawkes_runner import run_fawkes
        # result_path = await run_fawkes(file_path)
        
        # Placeholder - simulate processing
        import asyncio
        await asyncio.sleep(2)
        
        output_dir = "/app/data/outputs"
        os.makedirs(output_dir, exist_ok=True)
        result_path = f"{output_dir}/{job_id}_protected.png"
        
        # For now, just copy the file
        import shutil
        shutil.copy(file_path, result_path)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result_url"] = f"/api/protect/download/{job_id}"
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@router.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download protected image"""
    from fastapi.responses import FileResponse
    
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Result not available")
    
    result_path = f"/app/data/outputs/{job_id}_protected.png"
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(result_path, filename=f"protected_{job_id}.png")
