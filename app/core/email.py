from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import *

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)

async def send_email(receiver: str, subject: str, body: str):

    message = MessageSchema(
        subject=subject,
        recipients=[receiver],
        body=body,
        subtype="html"
    )

    fm = FastMail(conf)

    await fm.send_message(message)