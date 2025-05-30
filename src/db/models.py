from enum import IntEnum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class AdminApprovalStatus(IntEnum):
    PENDING = 0
    APPROVED = 1
    REJECTED = -1


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True, unique=False)
    submit_username = Column(String(255), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_admin = Column(Boolean, default=False)   
    phone_number = Column(String(20))
    inserted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    advertisements = relationship("Advertisement", back_populates="user")


class Advertisement(Base):
    __tablename__ = 'advertisements'

    adv_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    advertisement_type = Column(String(100), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    color = Column(String(50))
    function = Column(String(50))
    insurance = Column(String(50))
    exchange = Column(String(50))
    motor = Column(String(50))
    body = Column(String(50))
    chassis = Column(String(50))
    technical = Column(String(50))
    gearbox = Column(String(50))
    admin_approved_status = Column(Integer, default=AdminApprovalStatus.PENDING)
    money = Column(String(50))
    inserted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    more_detail = Column(String(50), default=" ", nullable=True)

    user = relationship("User", back_populates="advertisements")
    photos = relationship(
        "AdvertisementPhoto",
        back_populates="advertisement",
        cascade="all, delete-orphan")


class AdvertisementPhoto(Base):
    __tablename__ = 'advertisement_photos'

    photo_id = Column(Integer, primary_key=True)
    photo_path = Column(String(255))
    advertisement_id = Column(Integer, ForeignKey('advertisements.adv_id'))
    advertisement = relationship("Advertisement", back_populates="photos")
