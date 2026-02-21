from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.db.models import Attendance, Employee, AttendanceStatus
from app.schemas.schemas import AttendanceCreate, AttendanceOut, DashboardOut
from app.utils.security import get_current_admin

router = APIRouter(tags=["Attendance"])

@router.get("", response_model=List[AttendanceOut])
def list_attendance(
    employee_id: Optional[str] = Query(None),
    date_filter: Optional[date] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    q = db.query(Attendance, Employee.full_name, Employee.department)\
          .join(Employee, Attendance.employee_id == Employee.id)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    if date_filter:
        q = q.filter(Attendance.date == date_filter)
    if department:
        q = q.filter(Employee.department == department)
    if status and status in ("Present", "Absent"):
        q = q.filter(Attendance.status == AttendanceStatus(status))
    q = q.order_by(Attendance.date.desc())
    results = []
    for att, full_name, dept in q.all():
        results.append(AttendanceOut(
            id=att.id,
            employee_id=att.employee_id,
            date=att.date,
            status=att.status.value,
            full_name=full_name,
            department=dept
        ))
    return results

@router.post("", status_code=201)
def mark_attendance(att: AttendanceCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    emp = db.query(Employee).filter(Employee.id == att.employee_id).first()
    if not emp:
        raise HTTPException(404, detail="Employee not found")
    existing = db.query(Attendance).filter(
        Attendance.employee_id == att.employee_id,
        Attendance.date == att.date
    ).first()
    if existing:
        existing.status = AttendanceStatus(att.status)
        db.commit()
        return {"message": "Attendance updated"}
    db_att = Attendance(
        employee_id=att.employee_id,
        date=att.date,
        status=AttendanceStatus(att.status)
    )
    db.add(db_att)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Attendance already marked for this date")
    return {"message": "Attendance marked successfully"}

@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    today = date.today()
    total_employees = db.query(Employee).count()
    present_today = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.status == AttendanceStatus.present
    ).count()
    absent_today = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.status == AttendanceStatus.absent
    ).count()
    dept_rows = db.query(Employee.department, func.count().label('count'))\
                  .group_by(Employee.department).all()
    departments = [{"department": r.department, "count": r.count} for r in dept_rows]
    return DashboardOut(
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        departments=departments
    )
