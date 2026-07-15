from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    phone = Column(String(20), nullable=False)

    role = Column(String(20), default="user")

    patients = relationship(
        "Patient",
        back_populates="user",
        cascade="all, delete"
    )

    emergencies = relationship(
        "Emergency",
        back_populates="user",
        cascade="all, delete"
    )