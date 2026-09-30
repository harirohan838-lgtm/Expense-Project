from datetime import date, datetime, timedelta
import os
from pathlib import Path
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL is used in production. SQLite remains available for local development.
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(
        f"sqlite:///{BASE_DIR / 'expense_db.sqlite3'}",
        connect_args={"check_same_thread": False},
    )


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False, default="employee")
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    department = Column(String(100), nullable=True)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    receipt_filename = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


Base.metadata.create_all(engine)

SECRET_KEY = os.getenv("SECRET_KEY", "expense-report-demo-secret-change-in-production")
ALGORITHM = "HS256"

app = FastAPI(title="Expense Report System API", version="1.0.0")
security = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    with Session(engine) as session:
        employees = [
            ("Jeevitha", "jeevitha@beeja.com", "Sales"),
            ("Manoj", "manoj@beeja.com", "Operations"),
            ("Kavya", "kavya@beeja.com", "Finance"),
            ("Karunya", "karunya@beeja.com", "HR"),
            ("Akshaya", "akshaya@beeja.com", "Marketing"),
            ("Pranaya", "pranaya@beeja.com", "Technology"),
            ("Amit Employee", "amit@beeja.com", "Sales"),
            ("Neha Employee", "neha@beeja.com", "Operations"),
            ("Rahul Employee", "rahul@beeja.com", "Finance"),
        ]
        existing = {e.email.lower() for e in session.scalars(select(Employee)).all()}
        for name, email, department in employees:
            if email.lower() not in existing:
                session.add(Employee(name=name, email=email, role="employee", department=department))
        session.commit()


init_db()


class LoginRequest(BaseModel):
    email: str
    role: str = "employee"


class ExpenseCreate(BaseModel):
    title: str
    category: str
    amount: float = Field(gt=0)
    expense_date: str
    description: Optional[str] = ""
    receipt_filename: Optional[str] = ""


def create_token(employee_id: int):
    payload = {"sub": str(employee_id), "exp": datetime.utcnow() + timedelta(hours=8)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_employee(credentials: Optional[HTTPAuthorizationCredentials]):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    with Session(engine) as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=401, detail="Employee not found")
        return {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "department": employee.department,
        }


def expense_dict(expense: Expense):
    return {
        "id": expense.id,
        "employee_id": expense.employee_id,
        "title": expense.title,
        "category": expense.category,
        "amount": expense.amount,
        "expense_date": expense.expense_date,
        "description": expense.description or "",
        "receipt_filename": expense.receipt_filename or "",
        "status": expense.status,
        "created_at": expense.created_at.isoformat(timespec="seconds"),
        "updated_at": expense.updated_at.isoformat(timespec="seconds"),
    }


@app.get("/")
def root():
    return {"message": "Expense Report System API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest):
    with Session(engine) as session:
        employee = session.scalar(
            select(Employee).where(
                Employee.email.ilike(request.email.strip()),
                Employee.role == request.role,
            )
        )
        if not employee:
            raise HTTPException(status_code=401, detail="Employee email not found")
        return {
            "token": create_token(employee.id),
            "user": {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "role": employee.role,
                "department": employee.department,
            },
        }


@app.get("/expenses")
def list_expenses(
    employee_id: Optional[int] = Query(default=None),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    employee = get_current_employee(credentials)
    if employee_id is not None and employee_id != employee["id"]:
        raise HTTPException(status_code=403, detail="You can only view your own expenses")
    with Session(engine) as session:
        rows = session.scalars(
            select(Expense)
            .where(Expense.employee_id == employee["id"])
            .order_by(Expense.id.desc())
        ).all()
        return [expense_dict(row) for row in rows]


@app.post("/expenses")
def create_expense(
    expense: ExpenseCreate,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    employee = get_current_employee(credentials)
    try:
        date.fromisoformat(expense.expense_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="expense_date must be YYYY-MM-DD")

    now = datetime.now()
    new_expense = Expense(
        employee_id=employee["id"],
        title=expense.title.strip(),
        category=expense.category,
        amount=expense.amount,
        expense_date=expense.expense_date,
        description=expense.description or "",
        receipt_filename=expense.receipt_filename or "",
        status="draft",
        created_at=now,
        updated_at=now,
    )
    with Session(engine) as session:
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return expense_dict(new_expense)


@app.get("/expenses/{expense_id}")
def get_expense(
    expense_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    employee = get_current_employee(credentials)
    with Session(engine) as session:
        expense = session.scalar(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.employee_id == employee["id"],
            )
        )
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense_dict(expense)


@app.post("/expenses/{expense_id}/submit")
def submit_expense(
    expense_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    employee = get_current_employee(credentials)
    with Session(engine) as session:
        expense = session.scalar(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.employee_id == employee["id"],
            )
        )
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        if expense.status not in ("draft", "rejected"):
            raise HTTPException(
                status_code=400,
                detail=f"Expense cannot be submitted from status '{expense.status}'",
            )
        expense.status = "submitted"
        expense.updated_at = datetime.now()
        session.commit()
        session.refresh(expense)
        return expense_dict(expense)
