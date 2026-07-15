from pydantic import BaseModel, ConfigDict


class AmbulanceBase(BaseModel):
    vehicle_number: str
    driver_id: int
    status: str
    latitude: float
    longitude: float


class AmbulanceCreate(AmbulanceBase):
    pass


class AmbulanceLocationUpdate(BaseModel):
    latitude: float
    longitude: float


class AmbulanceResponse(AmbulanceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)