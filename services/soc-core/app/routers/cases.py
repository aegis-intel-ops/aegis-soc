from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db, Case, Client
from schemas import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter()

@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all cases with optional filters"""
    query = db.query(Case)
    
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    
    cases = query.order_by(Case.created_at.desc()).all()
    
    result = []
    for case in cases:
        result.append({
            "id": case.id,
            "client_id": case.client_id,
            "title": case.title,
            "description": case.description,
            "status": case.status,
            "priority": case.priority,
            "assigned_to": case.assigned_to,
            "created_at": case.created_at,
            "closed_at": case.closed_at,
            "alert_count": len(case.alerts)
        })
    
    return result

@router.post("/", response_model=CaseResponse)
async def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    """Create a new case"""
    # Verify client exists if provided
    if case.client_id:
        client = db.query(Client).filter(Client.id == case.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    db_case = Case(
        client_id=case.client_id,
        title=case.title,
        description=case.description,
        priority=case.priority.value,
        assigned_to=case.assigned_to
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    return {
        **db_case.__dict__,
        "alert_count": 0
    }

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get a specific case with alerts"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        **case.__dict__,
        "alert_count": len(case.alerts)
    }

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    update: CaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            if hasattr(value, 'value'):
                setattr(case, key, value.value)
            else:
                setattr(case, key, value)
    
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    
    return {
        **case.__dict__,
        "alert_count": len(case.alerts)
    }

@router.post("/{case_id}/close")
async def close_case(case_id: str, db: Session = Depends(get_db)):
    """Close a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = "closed"
    case.closed_at = datetime.utcnow()
    case.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Case closed", "id": case_id}

@router.get("/{case_id}/alerts")
async def get_case_alerts(case_id: str, db: Session = Depends(get_db)):
    """Get all alerts for a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return [
        {
            "id": alert.id,
            "source": alert.source,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "severity": alert.severity,
            "acknowledged": alert.acknowledged,
            "created_at": alert.created_at
        }
        for alert in case.alerts
    ]

@router.get("/stats/overview")
async def get_case_stats(db: Session = Depends(get_db)):
    """Get case statistics"""
    cases = db.query(Case).all()
    
    by_status = {}
    by_priority = {}
    
    for case in cases:
        by_status[case.status] = by_status.get(case.status, 0) + 1
        by_priority[case.priority] = by_priority.get(case.priority, 0) + 1
    
    return {
        "total": len(cases),
        "by_status": by_status,
        "by_priority": by_priority
    }
