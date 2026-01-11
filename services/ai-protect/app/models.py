from pydantic import BaseModel
from typing import Optional
from enum import Enum
import uuid
import time

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(str, Enum):
    FAWKES = "fawkes"
    MIST = "mist"
    PHOTOGUARD = "photoguard"

class Job(BaseModel):
    id: str
    type: JobType
    status: JobStatus
    created_at: float
    completed_at: Optional[float] = None
    input_path: str
    output_path: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def create(cls, job_type: JobType, input_path: str):
        return cls(
            id=str(uuid.uuid4()),
            type=job_type,
            status=JobStatus.PENDING,
            created_at=time.time(),
            input_path=input_path
        )
