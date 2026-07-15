from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse
from app.core.dependencies import get_current_user

router = APIRouter()


# Create Patient
@router.post("/add", response_model=PatientResponse)
def add_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID not found in authentication token"
        )

    db_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone,
        address=patient.address,
        blood_group=patient.blood_group,
        user_id=user_id
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    return db_patient


# Get Logged-in User's Patients
@router.get("/", response_model=list[PatientResponse])
def get_all_patients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    patients = db.query(Patient).filter(
        Patient.user_id == current_user["id"]
    ).all()

    return patients


# Get Patient By ID
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# Update Patient
@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    updated: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID not found in authentication token"
        )

    patient.user_id = user_id
    patient.name = updated.name
    patient.age = updated.age
    patient.blood_group = updated.blood_group
    patient.gender = updated.gender
    patient.phone = updated.phone
    patient.address = updated.address

    db.commit()
    db.refresh(patient)

    return patient


# Delete Patient
@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }