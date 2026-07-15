from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Register all models
from app.models import *

from app.routes.user import router as user_router
from app.routes.auth import router as auth_router
from app.routes.patient import router as patient_router
from app.routes.driver import router as driver_router
from app.routes.ambulance import router as ambulance_router
from app.routes.hospital import router as hospital_router
from app.routes.emergency import router as emergency_router
from app.routes.email import router as email_router
from app.routes.audit import router as audit_router
from app.routes.tracking import router as tracking_router
from app.routes.websocket import router as websocket_router

app = FastAPI(
    title="AI Ambulance System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. User
app.include_router(
    user_router,
    prefix="/user",
    tags=["User"]
)

# 2. Authentication
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# 3. Patient
app.include_router(
    patient_router,
    prefix="/patient",
    tags=["Patient"]
)

# 4. Driver
app.include_router(
    driver_router,
    prefix="/driver",
    tags=["Driver"]
)

# 5. Ambulance
app.include_router(
    ambulance_router,
    prefix="/ambulance",
    tags=["Ambulance"]
)

# 6. Hospital
app.include_router(
    hospital_router,
    prefix="/hospital",
    tags=["Hospital"]
)

# 7. Emergency
app.include_router(
    emergency_router,
    prefix="/emergency",
    tags=["Emergency"]
)

# 8. Email
app.include_router(
    email_router,
    prefix="/email",
    tags=["Email"]
)
# 9. Audit
app.include_router(
    audit_router,
    prefix="/audit",
    tags=["Audit Logs"]
)

# 10. Track
app.include_router(tracking_router)

app.include_router(websocket_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "AI Ambulance System Backend Running"
    }


@app.on_event("startup")
def seed_database():
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.driver import Driver
    from app.models.hospital import Hospital
    from app.models.ambulance import Ambulance
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        # 1. Seed Admin
        admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not admin:
            admin = User(
                full_name="System Admin",
                email="admin@gmail.com",
                password=hash_password("admin"),
                phone="1234567890",
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # 2. Seed Driver
        driver_user = db.query(User).filter(User.email == "driver@gmail.com").first()
        if not driver_user:
            driver_user = User(
                full_name="John Driver",
                email="driver@gmail.com",
                password=hash_password("driver"),
                phone="9876543210",
                role="driver"
            )
            db.add(driver_user)
            db.commit()
            db.refresh(driver_user)

        driver_rec = db.query(Driver).filter(Driver.email == "driver@gmail.com").first()
        if not driver_rec:
            driver_rec = Driver(
                name="John Driver",
                email="driver@gmail.com",
                password=hash_password("driver"),
                phone="9876543210",
                license_number="DL-12345",
                experience=5,
                status="Available"
            )
            db.add(driver_rec)
            db.commit()
            db.refresh(driver_rec)
        else:
            driver_rec.status = "Available"
            db.commit()

        # 3. Seed Hospital
        hospital = db.query(Hospital).filter(Hospital.name == "City General Hospital").first()
        if not hospital:
            hospital = Hospital(
                name="City General Hospital",
                address="123 Health Ave, Bangalore",
                phone="080-123456",
                available_beds=10,
                latitude="12.9716",
                longitude="77.5946"
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)

        # 4. Seed Ambulance
        ambulance = db.query(Ambulance).filter(Ambulance.vehicle_number == "KA-01-AMB-2026").first()
        if not ambulance:
            ambulance = Ambulance(
                vehicle_number="KA-01-AMB-2026",
                driver_id=driver_rec.id,
                status="Available",
                latitude=12.9716,
                longitude=77.5946
            )
            db.add(ambulance)
            db.commit()
        else:
            ambulance.driver_id = driver_rec.id
            ambulance.status = "Available"
            db.commit()

    finally:
        db.close()