from fastapi import APIRouter
from app.schemas.email import EmailSchema
from app.core.email import send_email

router = APIRouter()


@router.post("/send")
async def send_test_email(data: EmailSchema):

    await send_email(
        receiver=data.email,
        subject=data.subject,
        body=data.body
    )

    return {
        "message": "Email sent successfully"
    }