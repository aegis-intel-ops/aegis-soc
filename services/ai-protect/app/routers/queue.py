from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import List, Dict, Optional
import shutil
import os
import time
import uuid
from models import Job, JobStatus, JobType

router = APIRouter()

# In-memory job store (replace with DB for production persistence)
jobs: Dict[str, Job] = {}
queue: List[str] = []

UPLOAD_DIR = "/app/data/uploads"
OUTPUT_DIR = "/app/data/outputs"

# Ensure dirs exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/add", response_model=Job)
async def add_job(type: JobType = Form(...), image: UploadFile = File(...)):
    """Add a new job to the queue (called by Dashboard)"""
    file_ext = image.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    job = Job.create(type, file_path)
    jobs[job.id] = job
    queue.append(job.id)
    
    return job

@router.get("/pending", response_model=Optional[Job])
async def get_pending_job():
    """Get the next pending job (called by Colab Worker)"""
    # Simple FIFO, but check if we have any "pending" jobs in the list
    # We iterate copy to allow modification if needed, though here we just look
    for job_id in queue:
        job = jobs.get(job_id)
        if job and job.status == JobStatus.PENDING:
            # Mark as processing
            job.status = JobStatus.PROCESSING
            return job
    return None

@router.get("/image/{job_id}")
async def get_job_image(job_id: str):
    """Download input image for a job (called by Colab Worker)"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return FileResponse(job.input_path)

@router.post("/complete/{job_id}")
async def complete_job(job_id: str, file: UploadFile = File(...)):
    """Upload result for a job (called by Colab Worker)"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Save output
    file_ext = file.filename.split('.')[-1]
    output_filename = f"processed_{job_id}.{file_ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    job.status = JobStatus.COMPLETED
    job.completed_at = time.time()
    job.output_path = output_path
    
    # Remove from queue list (it's done)
    if job_id in queue:
        queue.remove(job_id)
        
    return job

@router.post("/fail/{job_id}")
async def fail_job(job_id: str, reason: str = Form(...)):
    """Mark job as failed (called by Colab Worker)"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.FAILED
    job.error = reason
    job.completed_at = time.time()
    
    if job_id in queue:
        queue.remove(job_id)
        
    return job

@router.get("/status/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """Check status (called by Dashboard)"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """Download result image (called by Dashboard)"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED or not job.output_path:
        raise HTTPException(status_code=400, detail="Job not completed")
        
    return FileResponse(job.output_path)
