from pydantic import BaseModel, Field


class HospitalBase(BaseModel):

    name: str = Field(..., min_length=3)

    address: str

    phone: str

    available_beds: int

    latitude: str

    longitude: str


class HospitalCreate(HospitalBase):
    pass


class HospitalResponse(HospitalBase):

    id: int

    class Config:
        from_attributes = True