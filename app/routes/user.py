from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.audit import save_log

from app.schemas.user import (
    UserCreate,
    UserResponse,
    ProfileUpdate
)

from app.core.security import hash_password
from app.core.roles import admin_required
from app.core.dependencies import get_current_user

router = APIRouter()


# -----------------------------
# Register User (Public)
# -----------------------------
@router.post("/add", response_model=UserResponse)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone,
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if db_user.role == "driver":
        from app.models.driver import Driver
        existing_driver = db.query(Driver).filter(Driver.email == db_user.email).first()
        if not existing_driver:
            db_driver = Driver(
                name=db_user.full_name,
                email=db_user.email,
                password=db_user.password,
                phone=db_user.phone,
                license_number=user.license_number or f"LIC-{db_user.phone}",
                experience=user.experience or 5,
                status="Available"
            )
            db.add(db_driver)
            db.commit()

    save_log(
        db=db,
        action="User Registered",
        user=db_user.email,
        details=db_user.full_name
)

    return db_user


# -----------------------------
# Get All Users (Admin)
# -----------------------------
@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    return db.query(User).all()


# -----------------------------
# Get User By ID (Admin)
# -----------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# -----------------------------
# Update User (Admin)
# -----------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    duplicate = db.query(User).filter(
        User.email == updated.email,
        User.id != user_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user.full_name = updated.full_name
    user.email = updated.email
    user.password = hash_password(updated.password)
    user.phone = updated.phone
    user.role = updated.role

    db.commit()
    db.refresh(user)

    return user


# -----------------------------
# Delete User (Admin)
# -----------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }


# -----------------------------
# Update Profile (Authenticated User)
# -----------------------------
@router.put("/profile/update", response_model=UserResponse)
def update_profile(
    updated: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == current_user["id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if updated.email is not None and updated.email != user.email:
        duplicate = db.query(User).filter(
            User.email == updated.email
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
        user.email = updated.email

    if updated.full_name is not None:
        user.full_name = updated.full_name

    if updated.phone is not None:
        user.phone = updated.phone

    if updated.password is not None:
        user.password = hash_password(updated.password)

    if updated.role is not None:
        user.role = updated.role
        if user.role == "driver":
            from app.models.driver import Driver
            existing_driver = db.query(Driver).filter(Driver.email == user.email).first()
            if not existing_driver:
                db_driver = Driver(
                    name=user.full_name,
                    email=user.email,
                    password=user.password,
                    phone=user.phone,
                    license_number=f"LIC-{user.phone}",
                    experience=5,
                    status="Available"
                )
                db.add(db_driver)

    db.commit()
    db.refresh(user)

    save_log(
        db=db,
        action="Profile Updated",
        user=user.email,
        details=f"User ID {user.id} updated their profile"
    )

    return user