from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.driver import Driver
from app.core.audit import save_log

from app.schemas.driver import (
    DriverCreate,
    DriverResponse
)

from app.core.roles import admin_required, driver_required

router = APIRouter()


# -----------------------------
# Create Driver (Admin Only)
# -----------------------------
@router.post("/add", response_model=DriverResponse)
def add_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    existing = db.query(Driver).filter(
        Driver.license_number == driver.license_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="License number already exists"
        )

    db_driver = Driver(
        name=driver.name,
        email=driver.email,
        password=driver.password,
        phone=driver.phone,
        license_number=driver.license_number,
        experience=driver.experience,
        status=driver.status
    )

    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)

    return db_driver


# -----------------------------
# Get All Drivers
# -----------------------------
@router.get("/", response_model=list[DriverResponse])
def get_all_drivers(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    return db.query(Driver).all()


# -----------------------------
# Get Logged-in Driver Profile
# -----------------------------
@router.get("/profile/me")
def get_driver_profile(
    db: Session = Depends(get_db),
    current_user=Depends(driver_required)
):
    driver = db.query(Driver).filter(
        Driver.email == current_user["sub"]
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver profile not found"
        )

    # Fetch assigned ambulance
    from app.models.ambulance import Ambulance
    ambulance = db.query(Ambulance).filter(
        Ambulance.driver_id == driver.id
    ).first()

    # Convert to dict to avoid serialization issues
    return {
        "driver": {
            "id": driver.id,
            "name": driver.name,
            "email": driver.email,
            "phone": driver.phone,
            "license_number": driver.license_number,
            "experience": driver.experience,
            "status": driver.status
        },
        "ambulance": {
            "id": ambulance.id,
            "vehicle_number": ambulance.vehicle_number,
            "status": ambulance.status,
            "latitude": ambulance.latitude,
            "longitude": ambulance.longitude
        } if ambulance else None
    }


# -----------------------------
# Get Driver By ID
# -----------------------------
@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    driver = db.query(Driver).filter(
        Driver.id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    return driver


# -----------------------------
# Update Driver
# -----------------------------
@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    updated: DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    driver = db.query(Driver).filter(
        Driver.id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    duplicate = db.query(Driver).filter(
        Driver.license_number == updated.license_number,
        Driver.id != driver_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="License number already exists"
        )

    driver.name = updated.name
    driver.phone = updated.phone
    driver.license_number = updated.license_number
    driver.experience = updated.experience
    driver.status = updated.status

    db.commit()
    db.refresh(driver)

    return driver


# -----------------------------
# Delete Driver
# -----------------------------
@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    driver = db.query(Driver).filter(
        Driver.id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    db.delete(driver)
    db.commit()

    return {
        "message": "Driver deleted successfully"
    }