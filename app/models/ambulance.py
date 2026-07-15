from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_number = Column(String, unique=True, nullable=False)

    driver_id = Column(Integer, ForeignKey("drivers.id"))

    status = Column(String, default="Available")

    latitude = Column(Float)

    longitude = Column(Float)

    driver = relationship("Driver")