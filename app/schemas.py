from typing_extensions import Literal


try:
    from pydantic import BaseModel  # type: ignore[import]
except ImportError:
    class BaseModel:
        def __init__(self, **data):
            for name, value in data.items():
                setattr(self, name, value)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Literal["donor", "hospital"]

class LoginRequest(BaseModel):
    email: str
    password: str

class DonorCreate(BaseModel):
    name: str
    blood_group: str
    age: int
    phone: str
    address: str

 
class DonationCreate(BaseModel):
    donor_id: int
    blood_group: str
    units: int

class HospitalCreate(BaseModel):
    hospital_name: str
    address: str
    phone: str
    license_no: str

class BloodRequestCreate(BaseModel):
    hospital_id: int
    blood_group: str
    units: int

