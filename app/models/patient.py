from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    gender = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )

    address = Column(
        String,
        nullable=False
    )

    blood_group = Column(
        String,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="patients"
    )

    emergencies = relationship(
        "Emergency",
        back_populates="patient"
    )