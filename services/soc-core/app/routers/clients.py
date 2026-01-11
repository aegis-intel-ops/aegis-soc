from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db, Client
from schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()

@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all clients with optional filters"""
    query = db.query(Client)
    
    if status:
        query = query.filter(Client.status == status)
    if risk_level:
        query = query.filter(Client.risk_level == risk_level)
    
    clients = query.order_by(Client.created_at.desc()).all()
    
    # Add case count
    result = []
    for client in clients:
        client_dict = {
            "id": client.id,
            "name": client.name,
            "code_name": client.code_name,
            "email": client.email,
            "phone": client.phone,
            "risk_level": client.risk_level,
            "status": client.status,
            "notes": client.notes,
            "created_at": client.created_at,
            "case_count": len(client.cases)
        }
        result.append(client_dict)
    
    return result

@router.post("/", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    db_client = Client(
        name=client.name,
        code_name=client.code_name,
        email=client.email,
        phone=client.phone,
        risk_level=client.risk_level.value,
        notes=client.notes
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return {
        **db_client.__dict__,
        "case_count": 0
    }

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db: Session = Depends(get_db)):
    """Get a specific client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {
        **client.__dict__,
        "case_count": len(client.cases)
    }

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    update: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            if hasattr(value, 'value'):  # Enum
                setattr(client, key, value.value)
            else:
                setattr(client, key, value)
    
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    
    return {
        **client.__dict__,
        "case_count": len(client.cases)
    }

@router.delete("/{client_id}")
async def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Delete a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted", "id": client_id}

@router.get("/{client_id}/cases")
async def get_client_cases(client_id: str, db: Session = Depends(get_db)):
    """Get all cases for a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return [
        {
            "id": case.id,
            "title": case.title,
            "status": case.status,
            "priority": case.priority,
            "created_at": case.created_at
        }
        for case in client.cases
    ]
