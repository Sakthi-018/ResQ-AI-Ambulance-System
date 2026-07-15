from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def save_log(
    db: Session,
    action: str,
    user: str,
    details: str
):

    log = AuditLog(
        action=action,
        performed_by=user,
        details=details
    )

    db.add(log)
    db.commit()