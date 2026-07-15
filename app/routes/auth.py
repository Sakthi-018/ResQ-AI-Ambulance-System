from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.core.security import verify_password
from app.core.auth import create_access_token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    username_input = form_data.username
    user = db.query(User).filter(
        (User.email == username_input) |
        (User.phone == username_input) |
        (User.full_name == username_input) |
        (User.email.like(f"{username_input}@%"))
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
            "id": user.id,
            "name": user.full_name
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }