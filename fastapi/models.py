"""
데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


class Gender(str, enum.Enum):
    """성별 열거형"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    home_address = Column(String(500), nullable=False)
    home_latitude = Column(String(50), nullable=True)
    home_longitude = Column(String(50), nullable=True)
    work_address = Column(String(500), nullable=False)
    work_latitude = Column(String(50), nullable=True)
    work_longitude = Column(String(50), nullable=True)
    work_start_time = Column(String(10), nullable=False)  # HH:MM 형식
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


