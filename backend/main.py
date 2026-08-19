from datetime import date, datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expense_db.sqlite3"
SECRET_KEY = "expense-report-demo-secret-change-in-production"
ALGORITHM = "HS256"

app = FastAPI(title="Expense Report System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            manager_id INTEGER,
            department TEXT,
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            description TEXT,
            receipt_filename TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    employees = [
        ("Amit Employee", "amit@beeja.com", "employee", None, "Sales"),
        ("Neha Employee", "neha@beeja.com", "employee", None, "Operations"),
        ("Rahul Employee", "rahul@beeja.com", "employee", None, "Finance"),
    ]

    for employee in employees:
        cur.execute(
            """
            INSERT OR IGNORE INTO employees
            (name, email, role, manager_id, department)
            VALUES (?, ?, ?, ?, ?)
            """,
            employee,
        )

    conn.commit()
    conn.close()


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
    payload = {
        "sub": str(employee_id),
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_employee(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    conn = get_db()
    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()

    if not employee:
        raise HTTPException(status_code=401, detail="Employee not found")

    return employee


def expense_dict(row):
    return dict(row)


@app.get("/")
def root():
    return {
        "message": "Expense Report System API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest):
    conn = get_db()
    employee = conn.execute(
        "SELECT * FROM employees WHERE LOWER(email) = LOWER(?) AND role = ?",
        (request.email.strip(), request.role),
    ).fetchone()
    conn.close()

    if not employee:
        raise HTTPException(
            status_code=401,
            detail="Employee email not found",
        )

    token = create_token(employee["id"])

    return {
        "token": token,
        "user": {
            "id": employee["id"],
            "name": employee["name"],
            "email": employee["email"],
            "role": employee["role"],
            "department": employee["department"],
        },
    }


@app.get("/expenses")
def list_expenses(
    employee_id: Optional[int] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    employee = get_current_employee(authorization)

    # Employees can only see their own expenses.
    requested_id = employee["id"] if employee_id is None else employee_id

    if requested_id != employee["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own expenses",
        )

    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, employee_id, title, category, amount, expense_date,
               description, receipt_filename, status, created_at, updated_at
        FROM expenses
        WHERE employee_id = ?
        ORDER BY id DESC
        """,
        (employee["id"],),
    ).fetchall()
    conn.close()

    return [expense_dict(row) for row in rows]


@app.post("/expenses")
def create_expense(
    expense: ExpenseCreate,
    authorization: Optional[str] = Header(default=None),
):
    employee = get_current_employee(authorization)

    try:
        date.fromisoformat(expense.expense_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="expense_date must be YYYY-MM-DD",
        )

    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO expenses
        (employee_id, title, category, amount, expense_date,
         description, receipt_filename, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
        """,
        (
            employee["id"],
            expense.title.strip(),
            expense.category,
            expense.amount,
            expense.expense_date,
            expense.description or "",
            expense.receipt_filename or "",
            now,
            now,
        ),
    )
    expense_id = cur.lastrowid
    conn.commit()

    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()

    return expense_dict(row)


@app.get("/expenses/{expense_id}")
def get_expense(
    expense_id: int,
    authorization: Optional[str] = Header(default=None),
):
    employee = get_current_employee(authorization)

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND employee_id = ?",
        (expense_id, employee["id"]),
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense_dict(row)


@app.post("/expenses/{expense_id}/submit")
def submit_expense(
    expense_id: int,
    authorization: Optional[str] = Header(default=None),
):
    employee = get_current_employee(authorization)

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND employee_id = ?",
        (expense_id, employee["id"]),
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found")

    if row["status"] not in ("draft", "rejected"):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Expense cannot be submitted from status '{row['status']}'",
        )

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        UPDATE expenses
        SET status = 'submitted', updated_at = ?
        WHERE id = ? AND employee_id = ?
        """,
        (now, expense_id, employee["id"]),
    )
    conn.commit()

    updated = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()

    return expense_dict(updated)
