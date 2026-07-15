from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ambulance import Ambulance
from app.models.driver import Driver
from app.core.audit import save_log

from app.schemas.ambulance import (
    AmbulanceCreate,
    AmbulanceResponse,
    AmbulanceLocationUpdate
)

from app.core.roles import admin_required, driver_required, user_required
from app.core.dependencies import get_current_user

router = APIRouter()


# -----------------------------
# Create Ambulance (Admin Only)
# -----------------------------
@router.post("/add", response_model=AmbulanceResponse)
def add_ambulance(
    ambulance: AmbulanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    driver = db.query(Driver).filter(
        Driver.id == ambulance.driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    existing = db.query(Ambulance).filter(
        Ambulance.vehicle_number == ambulance.vehicle_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Vehicle number already exists"
        )

    db_ambulance = Ambulance(
    driver_id=ambulance.driver_id,
    vehicle_number=ambulance.vehicle_number,
    status=ambulance.status,
    latitude=ambulance.latitude,
    longitude=ambulance.longitude
    )

    db.add(db_ambulance)
    db.commit()
    db.refresh(db_ambulance)

    save_log(
        db=db,
        action="Ambulance Added",
        user=current_user["sub"],
        details=db_ambulance.vehicle_number
)

    return db_ambulance


# -----------------------------
# Get All Ambulances
# -----------------------------
@router.get("/", response_model=list[AmbulanceResponse])
def get_all_ambulances(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    return db.query(Ambulance).all()


# -----------------------------
# Get Ambulance By ID
# -----------------------------
@router.get("/{ambulance_id}", response_model=AmbulanceResponse)
def get_ambulance(
    ambulance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    return ambulance


# -----------------------------
# Update Ambulance
# -----------------------------
@router.put("/{ambulance_id}", response_model=AmbulanceResponse)
def update_ambulance(
    ambulance_id: int,
    updated: AmbulanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    driver = db.query(Driver).filter(
        Driver.id == updated.driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    duplicate = db.query(Ambulance).filter(
        Ambulance.vehicle_number == updated.vehicle_number,
        Ambulance.id != ambulance_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Vehicle number already exists"
        )

    ambulance.driver_id = updated.driver_id
    ambulance.vehicle_number = updated.vehicle_number
    ambulance.status = updated.status
    ambulance.latitude = updated.latitude
    ambulance.longitude = updated.longitude

    db.commit()
    db.refresh(ambulance)

    return ambulance


# -----------------------------
# Update Ambulance Live Location
# -----------------------------
@router.put("/location/{ambulance_id}")
def update_location(
    ambulance_id: int,
    location: AmbulanceLocationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(driver_required)
):

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulance.latitude = location.latitude
    ambulance.longitude = location.longitude

    db.commit()
    db.refresh(ambulance)

    return {
        "message": "Location updated successfully",
        "ambulance": ambulance
    }


# -----------------------------
# Delete Ambulance
# -----------------------------
@router.delete("/{ambulance_id}")
def delete_ambulance(
    ambulance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == ambulance_id
    ).first()

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    db.delete(ambulance)
    db.commit()

    return {
        "message": "Ambulance deleted successfully"
    }