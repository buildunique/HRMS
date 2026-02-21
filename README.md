# HRMS Lite 👥

Lightweight Human Resource Management System — FastAPI + SQLite + Jinja2 templates.

## Tech Stack
| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python FastAPI                    |
| Auth       | JWT (python-jose) + bcrypt        |
| Database   | SQLite via SQLAlchemy ORM         |
| Frontend   | HTML + CSS + Vanilla JS (Jinja2)  |
| Deployment | Render / Railway                  |

## Project Structure
```
Project/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/
│   │   ├── auth.py          # POST /api/auth/login
│   │   ├── employee.py      # CRUD /api/employees
│   │   └── attendance.py    # CRUD /api/attendance + dashboard
│   ├── db/
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   └── models.py        # Admin, Employee, Attendance models
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── utils/
│   │   └── security.py      # JWT + bcrypt helpers
│   └── templates/
│       └── index.html       # Full SPA frontend
├── static/                  # Static assets (CSS/JS if separated)
├── requirements.txt
└── hrms.db                  # Auto-created on first run
```

## Run Locally

```bash
# 1. Navigate to backend folder
cd Project/

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start server
uvicorn app.main:app --reload --port 8000

# 5. Open browser
open http://localhost:8000
```

## Default Login
- **Username:** `admin`
- **Password:** `admin123`

## API Endpoints

| Method | Endpoint                    | Auth | Description           |
|--------|-----------------------------|------|-----------------------|
| POST   | `/api/auth/login`           | ✗    | Get JWT token         |
| GET    | `/api/employees`            | ✓    | List all employees    |
| POST   | `/api/employees`            | ✓    | Add employee          |
| DELETE | `/api/employees/{id}`       | ✓    | Delete employee       |
| GET    | `/api/attendance`           | ✓    | List attendance       |
| POST   | `/api/attendance`           | ✓    | Mark attendance       |
| GET    | `/api/attendance/dashboard` | ✓    | Dashboard stats       |

## Deploy to Render
1. Push to GitHub
2. New **Web Service** → select repo
3. Root Directory: `Project`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Assumptions & Limitations
- SQLite used (zero config); swap to PostgreSQL for production via `DATABASE_URL` env var
- Single admin user (no registration flow)
- JWT tokens expire after 8 hours
- Attendance is upsert — marking twice on same date updates the record


