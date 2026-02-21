from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine, SessionLocal
from app.db.models import Admin
from app.utils.security import hash_password

from app.api import auth, employee, attendance

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="HRMS Lite")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Auto-create admin
db = SessionLocal()
if not db.query(Admin).filter(Admin.username == "admin").first():
    admin = Admin(username="admin", password=hash_password("admin123"))
    db.add(admin)
    db.commit()
db.close()

app.include_router(auth.router, prefix="/api/auth")
app.include_router(employee.router, prefix="/api/employees")
app.include_router(attendance.router, prefix="/api/attendance")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app/templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
