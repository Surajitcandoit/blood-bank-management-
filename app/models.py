from sqlalchemy import Column, Integer, String, ForeignKey, Date  # type: ignore[import]
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    role = Column(String, default="donor")


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String)

    blood_group = Column(String, nullable=False)

    age = Column(Integer)

    phone = Column(String)

    address = Column(String)

    last_donation_date = Column(String)


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    hospital_name = Column(String, nullable=False)

    address = Column(String)

    phone = Column(String)

    license_no = Column(String)


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True)

    donor_id = Column(
        Integer,
        ForeignKey("donors.id")
    )

    blood_group = Column(String)

    units = Column(Integer)

    donation_date = Column(Date)


class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    id = Column(Integer, primary_key=True)

    blood_group = Column(String)

    units = Column(Integer)

    collection_date = Column(Date)

    expiry_date = Column(Date)


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id")
    )

    blood_group = Column(String)

    units = Column(Integer)

    request_date = Column(Date)

    status = Column(String, default="Pending")


class Distribution(Base):
    __tablename__ = "distributions"

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(Integer)

    hospital_id = Column(Integer)

    blood_group = Column(String)

    units = Column(Integer)

    distribution_date = Column(Date)


