from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db, Alert, Case
from schemas import AlertCreate, AlertResponse, AlertStats

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    severity: Optional[str] = None,
    source: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List alerts with optional filters"""
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    if source:
        query = query.filter(Alert.source == source)
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "case_id": a.case_id,
            "source": a.source,
            "alert_type": a.alert_type,
            "message": a.message,
            "severity": a.severity,
            "acknowledged": a.acknowledged,
            "acknowledged_by": a.acknowledged_by,
            "created_at": a.created_at
        }
        for a in alerts
    ]

@router.post("/", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    # Verify case exists if provided
    if alert.case_id:
        case = db.query(Case).filter(Case.id == alert.case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
    
    db_alert = Alert(
        case_id=alert.case_id,
        source=alert.source,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity.value
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return {
        "id": db_alert.id,
        "case_id": db_alert.case_id,
        "source": db_alert.source,
        "alert_type": db_alert.alert_type,
        "message": db_alert.message,
        "severity": db_alert.severity,
        "acknowledged": db_alert.acknowledged,
        "acknowledged_by": db_alert.acknowledged_by,
        "created_at": db_alert.created_at
    }

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = "system",
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert acknowledged", "id": alert_id}

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted", "id": alert_id}

@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics"""
    alerts = db.query(Alert).all()
    
    by_severity = {}
    by_source = {}
    unacknowledged = 0
    
    for alert in alerts:
        by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
        by_source[alert.source] = by_source.get(alert.source, 0) + 1
        if not alert.acknowledged:
            unacknowledged += 1
    
    return {
        "total": len(alerts),
        "unacknowledged": unacknowledged,
        "by_severity": by_severity,
        "by_source": by_source
    }

@router.post("/bulk-acknowledge")
async def bulk_acknowledge(
    alert_ids: List[str],
    acknowledged_by: str = "system",
    db: Session = Depends(get_db)
):
    """Acknowledge multiple alerts"""
    count = 0
    for alert_id in alert_ids:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            count += 1
    
    db.commit()
    return {"message": f"Acknowledged {count} alerts"}
