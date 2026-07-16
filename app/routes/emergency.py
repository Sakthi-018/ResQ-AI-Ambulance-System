from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas.status import EmergencyStatusUpdate
from app.core.ai import (
    find_nearest_ambulance,
    find_nearest_hospital,
    predict_eta
)

from app.models.user import User
from app.models.patient import Patient
from app.models.ambulance import Ambulance
from app.models.hospital import Hospital
from app.models.emergency import Emergency


from app.schemas.emergency import (
    EmergencyCreate,
    EmergencyResponse
)

from app.core.roles import (
    admin_required,
    user_required,
    driver_required
)
from app.core.dependencies import get_current_user

from app.core.email import send_email
from app.core.audit import save_log
from app.websocket.notification import notify_driver
from app.websocket.notification import broadcast_status

router = APIRouter()


# ============================================================
# CREATE EMERGENCY
# ============================================================
@router.post("/add", response_model=EmergencyResponse)
async def add_emergency(
    emergency: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(user_required)
):

    # ------------------------
    # Check User
    # ------------------------
    user = db.query(User).filter(
        User.id == emergency.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # ------------------------
    # Check Patient
    # ------------------------
    patient = db.query(Patient).filter(
        Patient.id == emergency.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # ------------------------
    # Find Available Ambulances
    # ------------------------
    available_ambulances = db.query(Ambulance).filter(
        Ambulance.status == "Available"
    ).all()

    if not available_ambulances:
        raise HTTPException(
            status_code=404,
            detail="No ambulance available"
        )

    ambulance, ambulance_distance = find_nearest_ambulance(
        available_ambulances,
        emergency.pickup_latitude,
        emergency.pickup_longitude
    )
    eta = predict_eta(ambulance_distance)

    # ------------------------
    # Find Hospitals
    # ------------------------
    hospital = None
    hospital_distance = 0.0

    # Try to find selected hospital by name first
    if emergency.destination:
        hospital = db.query(Hospital).filter(
            Hospital.name == emergency.destination,
            Hospital.available_beds > 0
        ).first()
        if hospital:
            from app.core.ai import haversine
            hospital_distance = haversine(
                emergency.pickup_latitude,
                emergency.pickup_longitude,
                hospital.latitude,
                hospital.longitude
            )

    # Fallback to AI allocation if not found or out of beds
    if not hospital:
        available_hospitals = db.query(Hospital).filter(
            Hospital.available_beds > 0
        ).all()

        if not available_hospitals:
            raise HTTPException(
                status_code=404,
                detail="No hospital with available beds"
            )

        hospital, hospital_distance = find_nearest_hospital(
            available_hospitals,
            emergency.pickup_latitude,
            emergency.pickup_longitude
        )

    # ------------------------
    # Update Status
    # ------------------------
    ambulance.status = "Busy"
    hospital.available_beds -= 1

    # ------------------------
    # Create Emergency
    # ------------------------
    db_emergency = Emergency(
        user_id=emergency.user_id,
        patient_id=emergency.patient_id,

        ambulance_id=ambulance.id,
        hospital_id=hospital.id,

        pickup_location=emergency.pickup_location,
        pickup_latitude=emergency.pickup_latitude,
        pickup_longitude=emergency.pickup_longitude,

        destination=emergency.destination,

        emergency_type=emergency.emergency_type,

        status="Assigned"
    )

    db.add(db_emergency)
    db.commit()
    db.refresh(db_emergency)

    await notify_driver(
    f"""
🚑 NEW EMERGENCY

Emergency ID : {db_emergency.id}

Patient : {patient.name}

Pickup : {emergency.pickup_location}

Hospital : {hospital.name}

Ambulance : {ambulance.vehicle_number}

ETA : {eta} Minutes
"""
)

    # ------------------------
    # Send Email
    # ------------------------
    try:
        await send_email(
            receiver=user.email,
            subject="🚑 AI Ambulance System - Emergency Assigned",
            body=f"""
            <h2>Emergency Request Confirmed</h2>

            <p>Hello <b>{user.full_name}</b></p>

            <p>Your emergency request has been accepted.</p>

            <hr>

            <p><b>Emergency:</b> {emergency.emergency_type}</p>

            <p><b>Pickup:</b> {emergency.pickup_location}</p>

            <p><b>Destination:</b> {emergency.destination}</p>

            <p><b>Assigned Ambulance:</b> {ambulance.vehicle_number}</p>

            <p><b>Hospital:</b> {hospital.name}</p>

            <p><b>Ambulance Distance:</b> {ambulance_distance:.2f} KM</p>

            <p><b>Hospital Distance:</b> {hospital_distance:.2f} KM</p>

            <p><b>Estimated Arrival Time:</b> {eta} Minutes</p>

            <p><b>Status:</b> Assigned</p>

            <hr>

            <h3>Your ambulance is on the way.</h3>

            <p>Thank you for using AI Ambulance System.</p>
            """
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to send email notification: {e}")

    # ------------------------
    # Audit Log
    # ------------------------
    save_log(
        db=db,
        action="Emergency Created",
        user=current_user["sub"],
        details=f"Emergency ID {db_emergency.id}"
    )

    return {
    "id": db_emergency.id,
    "user_id": db_emergency.user_id,
    "patient_id": db_emergency.patient_id,
    "ambulance_id": db_emergency.ambulance_id,
    "hospital_id": db_emergency.hospital_id,
    "pickup_location": db_emergency.pickup_location,
    "pickup_latitude": db_emergency.pickup_latitude,
    "pickup_longitude": db_emergency.pickup_longitude,
    "destination": db_emergency.destination,
    "emergency_type": db_emergency.emergency_type,
    "status": db_emergency.status,
    "eta_minutes": eta
}


# ============================================================
# GET ALL EMERGENCIES
# ============================================================
@router.get("/", response_model=list[EmergencyResponse])
def get_all_emergencies(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    return db.query(Emergency).all()


# ============================================================
# GET ACTIVE EMERGENCY FOR DRIVER
# ============================================================
@router.get("/driver/active", response_model=EmergencyResponse)
def get_driver_active_emergency(
    db: Session = Depends(get_db),
    current_user=Depends(driver_required)
):
    from app.models.driver import Driver
    from app.models.ambulance import Ambulance

    # 1. Find Driver by email
    driver = db.query(Driver).filter(
        Driver.email == current_user["sub"]
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver profile not found"
        )

    # 2. Find Ambulance assigned to this Driver
    ambulance = db.query(Ambulance).filter(
        Ambulance.driver_id == driver.id
    ).first()

    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="No ambulance assigned to this driver"
        )

    # 3. Find active emergency for this ambulance (not Completed/Declined)
    emergency = db.query(Emergency).filter(
        Emergency.ambulance_id == ambulance.id,
        ~Emergency.status.in_(["Completed", "Declined", "Rejected"])
    ).first()

    if not emergency:
        raise HTTPException(
            status_code=404,
            detail="No active emergency assigned to this ambulance"
        )

    from app.core.ai import haversine
    try:
        dist = haversine(
            float(ambulance.latitude),
            float(ambulance.longitude),
            float(emergency.pickup_latitude),
            float(emergency.pickup_longitude)
        )
        emergency.eta_minutes = int(predict_eta(dist))
    except Exception:
        emergency.eta_minutes = 15

    return emergency


# ============================================================
# GET EMERGENCY
# ============================================================
@router.get("/{emergency_id}", response_model=EmergencyResponse)
def get_emergency(
    emergency_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(user_required)
):

    emergency = db.query(Emergency).filter(
        Emergency.id == emergency_id
    ).first()

    if not emergency:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found"
        )

    eta = None
    if emergency.ambulance_id and emergency.status not in ["Completed", "Declined", "Rejected"]:
        ambulance = db.query(Ambulance).filter(Ambulance.id == emergency.ambulance_id).first()
        if ambulance:
            from app.core.ai import haversine
            try:
                dist = haversine(
                    float(ambulance.latitude),
                    float(ambulance.longitude),
                    float(emergency.pickup_latitude),
                    float(emergency.pickup_longitude)
                )
                eta = int(predict_eta(dist))
            except Exception:
                eta = 15
    
    emergency.eta_minutes = eta
    return emergency


# ============================================================
# UPDATE EMERGENCY
# ============================================================
@router.put("/{emergency_id}", response_model=EmergencyResponse)
def update_emergency(
    emergency_id: int,
    updated: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(driver_required)
):

    emergency = db.query(Emergency).filter(
        Emergency.id == emergency_id
    ).first()

    if not emergency:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found"
        )

    emergency.pickup_location = updated.pickup_location
    emergency.pickup_latitude = updated.pickup_latitude
    emergency.pickup_longitude = updated.pickup_longitude

    emergency.destination = updated.destination

    emergency.emergency_type = updated.emergency_type

    emergency.status = "Completed"

    db.commit()
    db.refresh(emergency)

    save_log(
        db=db,
        action="Emergency Updated",
        user=current_user["sub"],
        details=f"Emergency ID {emergency.id} completed"
    )

    return emergency

# Update 

@router.put("/status/{emergency_id}")
async def update_emergency_status(
    emergency_id: int,
    update: EmergencyStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["role"] not in ["driver", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Driver or Admin role required."
        )

    emergency = db.query(Emergency).filter(
        Emergency.id == emergency_id
    ).first()

    if not emergency:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found"
        )

    ambulance = db.query(Ambulance).filter(
        Ambulance.id == emergency.ambulance_id
    ).first()

    driver = None
    if ambulance:
        from app.models.driver import Driver
        driver = db.query(Driver).filter(Driver.id == ambulance.driver_id).first()

    emergency.status = update.status

    if update.status == "Driver Accepted":
        emergency.accepted_at = datetime.utcnow()
        if ambulance:
            ambulance.status = "Busy"
        if driver:
            driver.status = "Busy"

    elif update.status in ["Driver Rejected", "Declined", "Rejected"]:
        emergency.status = "Declined"
        if ambulance:
            ambulance.status = "Available"
        if driver:
            driver.status = "Available"

    elif update.status == "Reached Patient":
        emergency.reached_patient_at = datetime.utcnow()
        if driver:
            driver.status = "Reached Patient"

    elif update.status == "Reached Hospital":
        emergency.reached_hospital_at = datetime.utcnow()
        if driver:
            driver.status = "Reached Hospital"

    elif update.status == "Completed":
        emergency.completed_at = datetime.utcnow()
        if ambulance:
            ambulance.status = "Available"
        if driver:
            driver.status = "Available"

    db.commit()
    db.refresh(emergency)

    await broadcast_status(
    emergency.id,
    emergency.status
)

    return {
        "message": "Emergency status updated successfully",
        "status": emergency.status
    }


# ============================================================
# DELETE EMERGENCY
# ============================================================
@router.delete("/{emergency_id}")
def delete_emergency(
    emergency_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    emergency = db.query(Emergency).filter(
        Emergency.id == emergency_id
    ).first()

    if not emergency:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found"
        )

    # ← INSERT HERE
    ambulance = db.query(Ambulance).filter(
        Ambulance.id == emergency.ambulance_id
    ).first()

    if ambulance:
        ambulance.status = "Available"

    db.delete(emergency)
    db.commit()

    save_log(
        db=db,
        action="Emergency Deleted",
        user=current_user["sub"],
        details=f"Emergency ID {emergency_id} deleted"
    )

    return {
        "message": "Emergency deleted successfully"
    }