from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import date, datetime

# Auth
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Employee
class EmployeeCreate(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    department: str

    @validator('id', 'full_name', 'department')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None

    @validator('full_name', 'department', pre=True, always=False)
    def not_empty(cls, v):
        if v is not None and not str(v).strip():
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v

class EmployeeOut(BaseModel):
    id: str
    full_name: str
    email: str
    department: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

# Attendance
class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: Literal["Present", "Absent"]

class AttendanceOut(BaseModel):
    id: int
    employee_id: str
    date: date
    status: str
    full_name: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True

# Dashboard
class DashboardOut(BaseModel):
    total_employees: int
    present_today: int
    absent_today: int
    departments: list
