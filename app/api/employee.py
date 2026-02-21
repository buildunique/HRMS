from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Employee
from app.schemas.schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from app.utils.security import get_current_admin

router = APIRouter(tags=["Employees"])

@router.get("", response_model=List[EmployeeOut])
def list_employees(
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    q = db.query(Employee)
    if search:
        term = f"%{search.lower()}%"
        from sqlalchemy import or_, func
        q = q.filter(or_(
            func.lower(Employee.full_name).like(term),
            func.lower(Employee.email).like(term),
            func.lower(Employee.id).like(term),
        ))
    if department:
        q = q.filter(Employee.department == department)
    return q.order_by(Employee.full_name).all()

@router.get("/departments")
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    rows = db.query(Employee.department).distinct().order_by(Employee.department).all()
    return [r.department for r in rows]

@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    if db.query(Employee).filter(Employee.id == emp.id).first():
        raise HTTPException(400, detail="Employee ID already exists")
    if db.query(Employee).filter(Employee.email == emp.email).first():
        raise HTTPException(400, detail="Email address already exists")
    db_emp = Employee(**emp.dict())
    db.add(db_emp)
    try:
        db.commit()
        db.refresh(db_emp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Duplicate entry detected")
    return db_emp

@router.put("/{emp_id}", response_model=EmployeeOut)
def update_employee(emp_id: str, data: EmployeeUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, detail="Employee not found")
    # Check email uniqueness if changed
    if data.email and data.email != emp.email:
        if db.query(Employee).filter(Employee.email == data.email).first():
            raise HTTPException(400, detail="Email address already exists")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(emp, field, value)
    try:
        db.commit()
        db.refresh(emp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Update failed due to duplicate data")
    return emp

@router.delete("/{emp_id}", status_code=200)
def delete_employee(emp_id: str, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted successfully"}
