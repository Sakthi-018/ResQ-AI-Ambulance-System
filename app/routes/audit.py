from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.audit import AuditLog

from app.schemas.audit import AuditLogResponse

from app.core.roles import admin_required

router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
def get_logs(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    return db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()