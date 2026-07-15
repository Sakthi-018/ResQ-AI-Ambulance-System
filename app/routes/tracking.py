from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.websocket.notification import broadcast_location

from app.schemas.tracking import (
    LocationUpdate,
    LocationResponse
)

from app.services.tracking_service import (
    update_location,
    get_location
)

router = APIRouter(
    prefix="/tracking",
    tags=["Live Tracking"]
)


@router.put("/location/{id}",
            response_model=LocationResponse)
async def update_ambulance_location(
    id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db)
):

    ambulance = update_location(
        db,
        id,
        location.latitude,
        location.longitude
    )

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )
    await broadcast_location(
        ambulance.id,
        float(ambulance.latitude),
        float(ambulance.longitude)
)

    return ambulance


@router.get("/location/{id}",
            response_model=LocationResponse)
def get_ambulance_location(
    id: int,
    db: Session = Depends(get_db)
):

    ambulance = get_location(
        db,
        id
    )

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    return ambulance