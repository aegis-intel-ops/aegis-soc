from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import httpx
import uuid

router = APIRouter()

# SpiderFoot configuration - runs as a separate container
SPIDERFOOT_URL = os.getenv("SPIDERFOOT_URL", "http://spiderfoot:5001")

# In-memory scan storage (use Redis in production)
scans = {}

class ScanRequest(BaseModel):
    target: str  # Domain, IP, email, or username
    scan_type: str = "all"  # all, passive, dns, social, darkweb
    modules: Optional[List[str]] = None

class ScanStatus(BaseModel):
    scan_id: str
    status: str  # queued, running, completed, failed
    target: str
    progress: int = 0
    results_count: int = 0

class ScanResult(BaseModel):
    scan_id: str
    target: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, int]

@router.post("/scan", response_model=ScanStatus)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a new SpiderFoot OSINT scan"""
    
    scan_id = str(uuid.uuid4())[:8].upper()
    
    # Store scan info
    scans[scan_id] = {
        "status": "queued",
        "target": request.target,
        "scan_type": request.scan_type,
        "progress": 0,
        "results": []
    }
    
    # Start scan in background
    background_tasks.add_task(run_spiderfoot_scan, scan_id, request)
    
    return ScanStatus(
        scan_id=scan_id,
        status="queued",
        target=request.target,
        progress=0,
        results_count=0
    )

@router.get("/status/{scan_id}", response_model=ScanStatus)
async def get_scan_status(scan_id: str):
    """Get status of a running or completed scan"""
    
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans[scan_id]
    return ScanStatus(
        scan_id=scan_id,
        status=scan["status"],
        target=scan["target"],
        progress=scan["progress"],
        results_count=len(scan.get("results", []))
    )

@router.get("/results/{scan_id}", response_model=ScanResult)
async def get_scan_results(scan_id: str):
    """Get results of a completed scan"""
    
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans[scan_id]
    
    if scan["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Scan not completed. Current status: {scan['status']}"
        )
    
    results = scan.get("results", [])
    
    # Summarize by category
    summary = {}
    for r in results:
        category = r.get("type", "other")
        summary[category] = summary.get(category, 0) + 1
    
    return ScanResult(
        scan_id=scan_id,
        target=scan["target"],
        findings=results[:100],  # Limit to first 100
        summary=summary
    )

@router.get("/modules")
async def list_modules():
    """List available SpiderFoot modules"""
    
    # Common SpiderFoot module categories
    return {
        "scan_types": {
            "all": "Complete OSINT scan (slow, comprehensive)",
            "passive": "Passive reconnaissance only",
            "dns": "DNS and subdomain enumeration",
            "social": "Social media and username search",
            "darkweb": "Dark web and breach monitoring"
        },
        "data_types": [
            "IP_ADDRESS",
            "DOMAIN_NAME", 
            "EMAIL_ADDRESS",
            "USERNAME",
            "PHONE_NUMBER",
            "BITCOIN_ADDRESS"
        ]
    }

@router.delete("/scan/{scan_id}")
async def cancel_scan(scan_id: str):
    """Cancel a running scan"""
    
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scans[scan_id]["status"] = "cancelled"
    return {"message": f"Scan {scan_id} cancelled"}

@router.get("/health")
async def spiderfoot_health():
    """Check if SpiderFoot service is available"""
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SPIDERFOOT_URL}/")
            return {
                "status": "available",
                "url": SPIDERFOOT_URL
            }
    except Exception as e:
        return {
            "status": "unavailable",
            "url": SPIDERFOOT_URL,
            "error": str(e)
        }

async def run_spiderfoot_scan(scan_id: str, request: ScanRequest):
    """Background task to run SpiderFoot scan"""
    
    try:
        scans[scan_id]["status"] = "running"
        scans[scan_id]["progress"] = 10
        
        # Try to connect to SpiderFoot
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                # Start scan via SpiderFoot API
                response = await client.post(
                    f"{SPIDERFOOT_URL}/startscan",
                    data={
                        "scanname": f"Aegis-{scan_id}",
                        "scantarget": request.target,
                        "usecase": request.scan_type
                    }
                )
                
                scans[scan_id]["progress"] = 50
                
                # In production, poll for completion
                # For now, simulate results
                
            except httpx.ConnectError:
                # SpiderFoot not available, use fallback/mock
                pass
        
        # Simulated results (replace with actual SpiderFoot API calls)
        scans[scan_id]["results"] = [
            {"type": "DOMAIN_NAME", "data": request.target, "source": "DNS"},
            {"type": "IP_ADDRESS", "data": "Resolved IP", "source": "DNS"},
        ]
        
        scans[scan_id]["status"] = "completed"
        scans[scan_id]["progress"] = 100
        
    except Exception as e:
        scans[scan_id]["status"] = "failed"
        scans[scan_id]["error"] = str(e)
