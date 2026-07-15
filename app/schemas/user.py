from pydantic import BaseModel, EmailStr, Field
from typing import Annotated


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50)

    email: EmailStr

    phone: Annotated[str, Field(pattern=r"^\d{10}$")]

    role: str = "user"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    license_number: str | None = None
    experience: int | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=r"^\d{10}$")
    password: str | None = Field(None, min_length=6)
    role: str | None = None


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True