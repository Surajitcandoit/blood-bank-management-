try:
    from fastapi import FastAPI, Depends  # type: ignore[import]
except Exception:
    raise ImportError(
        "fastapi is not installed or cannot be resolved. Install with: pip install fastapi"
    )
from .database import Base, engine
from .models import (
    User,
    Donor,
    Hospital,
    Donation,
    BloodInventory,
    BloodRequest,
    Distribution
)
from .models import User
from datetime import date
from sqlalchemy import func
from .schemas import LoginRequest, DonorCreate, DonationCreate, HospitalCreate,BloodRequestCreate
from .auth import verify_password
from .security import create_access_token
from .dependencies import get_current_user
from .dependencies import admin_required
try:
    from sqlalchemy.orm import Session  # type: ignore[import]
except Exception:
    raise ImportError(
        "sqlalchemy is not installed or cannot be resolved. Install with: pip install sqlalchemy"
    )

from .database import SessionLocal
from .schemas import UserCreate
from .auth import hash_password
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to your Django URL in production, e.g., ["http://localhost:8000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Blood Bank System Running"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        allowed_roles = ["donor", "hospital"]
        if user.role not in allowed_roles:
            return {"error": "Invalid role requested. You cannot register as an admin."}
        
        existing = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing:
            return {"error": "Email already exists"}

        new_user = User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password),
            role=user.role
        )

        db.add(new_user)
        db.commit()

        return {"message": "Registration successful"}

    except Exception as e:
        return {"error": str(e)}

@app.post("/login")
def login(
    credentials: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == credentials.username).first()

    if not user:
        return {"error": "Invalid email"}
    if not verify_password(credentials.password, user.password):
        return {"error": "Wrong password"}

    token = create_access_token({"sub": user.email, "role": user.role})

    # UPDATE THIS RETURN BLOCK
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role  # <-- Pass the role to the frontend!
    }


@app.get("/profile")
def profile(
    user=Depends(get_current_user)
):

    return {
        "logged_user": user
    }

@app.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    try:

        total_users = db.query(User).count()

        total_donors = db.query(Donor).count()

        total_hospitals = db.query(Hospital).count()

        total_requests = db.query(BloodRequest).count()

        approved_requests = db.query(
            BloodRequest
        ).filter(
            BloodRequest.status == "Approved"
        ).count()

        pending_requests = db.query(
            BloodRequest
        ).filter(
            BloodRequest.status == "Pending"
        ).count()

        total_distributions = db.query(
            Distribution
        ).count()

        return {
            "total_users": total_users,
            "total_donors": total_donors,
            "total_hospitals": total_hospitals,
            "total_requests": total_requests,
            "approved_requests": approved_requests,
            "pending_requests": pending_requests,
            "total_distributions": total_distributions
        }

    except Exception as e:
        return {
            "error": str(e)
        }

@app.get("/admin/staff")
def get_staff(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    # Fetch all users who have the "admin" role
    admins = db.query(User).filter(User.role == "admin").all()
    return admins

@app.delete("/admin/staff/{user_id}")
def delete_staff(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    target_admin = db.query(User).filter(
        User.id == user_id, 
        User.role == "admin"
    ).first()

    if not target_admin:
        return {"error": "Admin not found"}

    # SAFETY CHECK: Prevent the admin from deleting their own account
    if target_admin.email == current_user["sub"]:
        return {"error": "You cannot delete your own account!"}

    db.delete(target_admin)
    db.commit()

    return {"message": "Admin removed successfully"}


@app.post("/donors")
def create_donor(
    donor: DonorCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    new_donor = Donor(
        name=donor.name,
        blood_group=donor.blood_group,
        age=donor.age,
        phone=donor.phone,
        address=donor.address
    )

    db.add(new_donor)
    db.commit()

    return {"message": "Donor added"}

@app.post("/donation/add")
def add_donation(
    donation: DonationCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    donation_record = Donation(
        donor_id=donation.donor_id,
        blood_group=donation.blood_group,
        units=donation.units,
        donation_date=date.today()
    )

    db.add(donation_record)

    inventory = BloodInventory(
        blood_group=donation.blood_group,
        units=donation.units,
        collection_date=date.today(),
        expiry_date=date.today()
    )

    db.add(inventory)

    db.commit()

    return {
        "message": "Donation recorded and inventory updated"
    }

@app.post("/hospital/create")
def create_hospital(
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    new_hospital = Hospital(
        hospital_name=hospital.hospital_name,
        address=hospital.address,
        phone=hospital.phone,
        license_no=hospital.license_no
    )

    db.add(new_hospital)
    db.commit()

    return {
        "message": "Hospital registered successfully"
    }

@app.get("/hospitals")
def get_hospitals(
    db: Session = Depends(get_db)
):
    return db.query(Hospital).all()

@app.post("/request-blood")
def request_blood(

    request: BloodRequestCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    blood_request = BloodRequest(
        hospital_id=request.hospital_id,
        blood_group=request.blood_group,
        units=request.units,
        request_date=date.today(),
        status="Pending"
    )

    db.add(blood_request)
    db.commit()

    return {
        "message": "Blood request submitted"
    }


@app.get("/requests")
def get_requests(
    db: Session = Depends(get_db)
):
    return db.query(BloodRequest).all()

@app.post("/request/{request_id}/approve")
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    blood_request = db.query(
        BloodRequest
    ).filter(
        BloodRequest.id == request_id
    ).first()

    if not blood_request:
        return {
            "error": "Request not found"
        }

    inventory = db.query(
        BloodInventory
    ).filter(
        BloodInventory.blood_group ==
        blood_request.blood_group
    ).first()

    if not inventory:
        return {
            "error": "Blood group not available"
        }

    if inventory.units < blood_request.units:
        return {
            "error": "Insufficient stock"
        }

    inventory.units -= blood_request.units

    blood_request.status = "Approved"

    distribution = Distribution(
        request_id=blood_request.id,
        hospital_id=blood_request.hospital_id,
        blood_group=blood_request.blood_group,
        units=blood_request.units,
        distribution_date=date.today()
    )

    db.add(distribution)

    db.commit()

    return {
        "message": "Request approved"
    }

@app.post("/request/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    blood_request = db.query(
        BloodRequest
    ).filter(
        BloodRequest.id == request_id
    ).first()

    if not blood_request:
        return {
            "error": "Request not found"
        }

    blood_request.status = "Rejected"

    db.commit()

    return {
        "message": "Request rejected"
    }

@app.get("/distributions")
def get_distributions(
    db: Session = Depends(get_db)
):

    return db.query(
        Distribution
    ).all()

@app.get("/donors")
def get_donors(
    db: Session = Depends(get_db)
):
    return db.query(Donor).all()


#search donors by blood group
@app.get("/donors/{blood_group}")
def search_donors(
    blood_group: str,
    db: Session = Depends(get_db)
):

    donors = db.query(Donor).filter(
        Donor.blood_group == blood_group
    ).all()

    return donors

@app.get("/inventory/low-stock")
def low_stock(
    db: Session = Depends(get_db)
):

    inventory = db.query(
        BloodInventory
    ).filter(
        BloodInventory.units < 5
    ).all()

    return inventory

@app.get("/inventory/summary")
def inventory_summary(
    db: Session = Depends(get_db)
):

    inventory = db.query(
        BloodInventory
    ).all()

    return inventory

@app.get("/inventory")
def get_inventory(
    db: Session = Depends(get_db)
):
    return db.query(
        BloodInventory
    ).all()


@app.get("/inventory/expired")
def expired_blood(
    db: Session = Depends(get_db)
):

    expired = db.query(
        BloodInventory
    ).filter(
        BloodInventory.expiry_date < date.today()
    ).all()

    return expired

@app.get("/test-admin")
def test_admin():
     return {"message": "Admin route work correctly"}

@app.delete("/donor/{donor_id}")
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    donor = db.query(Donor).filter(
        Donor.id == donor_id
    ).first()

    if not donor:
        return {"error": "Donor not found"}

    db.delete(donor)
    db.commit()

    return {"message": "Donor deleted"}

@app.delete("/hospital/{hospital_id}")
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):

    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        return {"error": "Hospital not found"}

    db.delete(hospital)
    db.commit()

    return {"message": "Hospital deleted"}

@app.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db)
):

    total_units = db.query(
        func.sum(BloodInventory.units)
    ).scalar() or 0

    return {
        "total_units": total_units,
        "total_donors": db.query(Donor).count(),
        "total_hospitals": db.query(Hospital).count(),
        "total_requests": db.query(BloodRequest).count(),
        "total_distributions": db.query(Distribution).count()
    }


