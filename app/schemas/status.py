from pydantic import BaseModel


class EmergencyStatusUpdate(BaseModel):
    status: str