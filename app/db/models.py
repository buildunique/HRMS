from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class AttendanceStatus(str, enum.Enum):
    present = "Present"
    absent = "Absent"

class Admin(Base):
    __tablename__ = "admins"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Employee(Base):
    __tablename__ = "employees"
    id         = Column(String, primary_key=True, index=True)
    full_name  = Column(String, nullable=False)
    email      = Column(String, unique=True, nullable=False, index=True)
    department = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    attendance = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendance"
    id          = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date        = Column(Date, nullable=False)
    status      = Column(Enum(AttendanceStatus), nullable=False)
    employee    = relationship("Employee", back_populates="attendance")

    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('employee_id', 'date', name='uq_emp_date'),
    )
