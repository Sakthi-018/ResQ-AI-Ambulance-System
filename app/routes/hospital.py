from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.hospital import Hospital

from app.schemas.hospital import (
    HospitalCreate,
    HospitalResponse
)

from app.core.roles import (
    admin_required,
    user_required
)
from app.core.dependencies import get_current_user

from app.core.audit import save_log

router = APIRouter()


# -----------------------------------
# Add Hospital
# -----------------------------------
@router.post("/add", response_model=HospitalResponse)
def add_hospital(
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    existing = db.query(Hospital).filter(
        Hospital.name == hospital.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Hospital already exists"
        )

    db_hospital = Hospital(
        name=hospital.name,
        address=hospital.address,
        phone=hospital.phone,
        available_beds=hospital.available_beds,
        latitude=hospital.latitude,
        longitude=hospital.longitude
    )

    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)

    save_log(
        db=db,
        action="Hospital Added",
        user=current_user["sub"],
        details=f"Hospital {hospital.name} added"
    )

    return db_hospital


# -----------------------------------
# Get All Hospitals
# -----------------------------------
@router.get("/", response_model=list[HospitalResponse])
def get_all_hospitals(
    db: Session = Depends(get_db),
    current_user=Depends(user_required)
):

    return db.query(Hospital).all()


# -----------------------------------
# Get Hospital By ID
# -----------------------------------
@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    return hospital


# -----------------------------------
# Update Hospital
# -----------------------------------
@router.put("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    updated: HospitalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    hospital.name = updated.name
    hospital.address = updated.address
    hospital.phone = updated.phone
    hospital.available_beds = updated.available_beds
    hospital.latitude = updated.latitude
    hospital.longitude = updated.longitude

    db.commit()
    db.refresh(hospital)

    save_log(
        db=db,
        action="Hospital Updated",
        user=current_user["sub"],
        details=f"Hospital {hospital.name} updated"
    )

    return hospital


# -----------------------------------
# Delete Hospital
# -----------------------------------
@router.delete("/{hospital_id}")
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    db.delete(hospital)
    db.commit()

    save_log(
        db=db,
        action="Hospital Deleted",
        user=current_user["sub"],
        details=f"Hospital ID {hospital_id} deleted"
    )

    return {
        "message": "Hospital deleted successfully"
    }