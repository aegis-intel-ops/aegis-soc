from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class ClientStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class CaseStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    closed = "closed"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Severity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"

# Client Schemas
class ClientCreate(BaseModel):
    name: str
    code_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.medium
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    code_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None

class ClientResponse(BaseModel):
    id: str
    name: str
    code_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    risk_level: str
    status: str
    notes: Optional[str]
    created_at: datetime
    case_count: int = 0

    class Config:
        from_attributes = True

# Case Schemas
class CaseCreate(BaseModel):
    client_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    assigned_to: Optional[str] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    priority: Optional[Priority] = None
    assigned_to: Optional[str] = None

class CaseResponse(BaseModel):
    id: str
    client_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]
    alert_count: int = 0

    class Config:
        from_attributes = True

# Alert Schemas
class AlertCreate(BaseModel):
    case_id: Optional[str] = None
    source: str
    alert_type: str
    message: str
    severity: Severity = Severity.info

class AlertResponse(BaseModel):
    id: str
    case_id: Optional[str]
    source: str
    alert_type: str
    message: str
    severity: str
    acknowledged: bool
    acknowledged_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AlertStats(BaseModel):
    total: int
    unacknowledged: int
    by_severity: dict
    by_source: dict
