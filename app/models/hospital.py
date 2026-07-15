from sqlalchemy import Column, Integer, String
from app.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    address = Column(String, nullable=False)

    phone = Column(String, unique=True, nullable=False)

    available_beds = Column(Integer, default=0)

    latitude = Column(String)

    longitude = Column(String)