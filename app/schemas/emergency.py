from pydantic import BaseModel


class EmergencyBase(BaseModel):

    user_id: int | None = None

    patient_id: int | None = None

    pickup_location: str | None = None

    pickup_latitude: str | None = None

    pickup_longitude: str | None = None

    destination: str | None = None

    emergency_type: str | None = None


class EmergencyCreate(EmergencyBase):
    pass

class EmergencyStatusUpdate(BaseModel):
    status: str


class EmergencyResponse(EmergencyBase):

    id: int

    ambulance_id: int | None = None

    hospital_id: int | None = None

    status: str | None = None

    eta_minutes: int | None = None

    class Config:
        from_attributes = True