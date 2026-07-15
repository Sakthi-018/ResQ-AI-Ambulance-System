from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Emergency(Base):
    __tablename__ = "emergencies"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    ambulance_id = Column(Integer, ForeignKey("ambulances.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))

    pickup_location = Column(String)

    pickup_latitude = Column(String)
    pickup_longitude = Column(String)

    destination = Column(String)

    emergency_type = Column(String)

    # Current status
    status = Column(String, default="Emergency Created")

    # Time tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    reached_patient_at = Column(DateTime, nullable=True)
    reached_hospital_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    patient = relationship("Patient")
    ambulance = relationship("Ambulance")
    hospital = relationship("Hospital")