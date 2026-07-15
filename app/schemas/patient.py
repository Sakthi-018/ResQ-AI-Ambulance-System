from pydantic import BaseModel


class PatientCreate(BaseModel):
    user_id: int
    name: str
    age: int
    blood_group: str
    gender: str
    phone: str
    address: str


class PatientResponse(PatientCreate):
    id: int

    class Config:
        from_attributes = True