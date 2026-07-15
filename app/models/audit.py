from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String)

    performed_by = Column(String)

    details = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)