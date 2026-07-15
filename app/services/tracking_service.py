from sqlalchemy.orm import Session
from app.models.ambulance import Ambulance


def update_location(
    db: Session,
    ambulance_id: int,
    latitude: float,
    longitude: float
):

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()

    if not ambulance:
        return None

    ambulance.latitude = latitude
    ambulance.longitude = longitude

    db.commit()
    db.refresh(ambulance)

    return ambulance


def get_location(
    db: Session,
    ambulance_id: int
):

    return db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()