from pydantic import BaseModel
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    action: str
    performed_by: str
    details: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True