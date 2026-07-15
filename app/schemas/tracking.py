from pydantic import BaseModel


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


class LocationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    status: str

    class Config:
        from_attributes = True