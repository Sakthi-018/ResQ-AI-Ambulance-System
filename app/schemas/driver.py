from pydantic import BaseModel, EmailStr


class DriverCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    license_number: str
    experience: int
    status: str


class DriverResponse(DriverCreate):
    id: int

    class Config:
        from_attributes = True