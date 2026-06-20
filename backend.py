from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI(title="Employee Leave Management System")

DB = "leave.db"


# =====================================================
# DATABASE SETUP
# =====================================================

def init_db():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # USERS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        manager_id INTEGER
    )
    """)

    # LEAVE BALANCES

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leave_balance(
        user_id INTEGER PRIMARY KEY,
        casual INTEGER DEFAULT 12,
        sick INTEGER DEFAULT 10,
        earned INTEGER DEFAULT 15
    )
    """)

    # LEAVES

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leaves(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        leave_type TEXT,
        start_date TEXT,
        end_date TEXT,
        days INTEGER,
        reason TEXT,
        status TEXT DEFAULT 'Pending',
        approved_by INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM users")

    count = cur.fetchone()[0]

    if count == 0:

        users = [

            (
                "Admin",
                "admin@company.com",
                "123",
                "admin",
                None
            ),

            (
                "Raj Manager",
                "raj@company.com",
                "123",
                "manager",
                None
            ),

            (
                "Priya Manager",
                "priya@company.com",
                "123",
                "manager",
                None
            ),

            (
                "John",
                "john@company.com",
                "123",
                "employee",
                2
            ),

            (
                "David",
                "david@company.com",
                "123",
                "employee",
                2
            ),

            (
                "Sarah",
                "sarah@company.com",
                "123",
                "employee",
                3
            ),

            (
                "Emma",
                "emma@company.com",
                "123",
                "employee",
                3
            )
        ]

        cur.executemany("""
        INSERT INTO users
        (name,email,password,role,manager_id)
        VALUES(?,?,?,?,?)
        """, users)

        conn.commit()

        cur.execute("SELECT id FROM users")

        all_users = cur.fetchall()

        for user in all_users:

            cur.execute("""
            INSERT INTO leave_balance
            (user_id,casual,sick,earned)
            VALUES(?,?,?,?)
            """,
            (
                user[0],
                12,
                10,
                15
            ))

        conn.commit()

    conn.close()


init_db()

# =====================================================
# MODELS
# =====================================================

class Login(BaseModel):
    email: str
    password: str


class EmployeeCreate(BaseModel):
    name: str
    email: str
    password: str
    manager_id: int


class ManagerCreate(BaseModel):
    name: str
    email: str
    password: str


class LeaveRequest(BaseModel):
    employee_id: int
    leave_type: str
    start_date: str
    end_date: str
    days: int
    reason: str


# =====================================================
# LOGIN
# =====================================================

@app.post("/login")
def login(data: Login):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name,role
    FROM users
    WHERE email=? AND password=?
    """,
    (
        data.email,
        data.password
    ))

    user = cur.fetchone()

    conn.close()

    if not user:

        return {
            "success": False
        }

    return {

        "success": True,
        "id": user[0],
        "name": user[1],
        "role": user[2]
    }


# =====================================================
# CREATE MANAGER
# =====================================================

@app.post("/create_manager")
def create_manager(data: ManagerCreate):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users
    (name,email,password,role)
    VALUES(?,?,?,'manager')
    """,
    (
        data.name,
        data.email,
        data.password
    ))

    manager_id = cur.lastrowid

    cur.execute("""
    INSERT INTO leave_balance
    (user_id)
    VALUES(?)
    """,
    (manager_id,))

    conn.commit()
    conn.close()

    return {
        "message": "Manager Created"
    }


# =====================================================
# CREATE EMPLOYEE
# =====================================================

@app.post("/create_employee")
def create_employee(data: EmployeeCreate):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users
    (name,email,password,role,manager_id)
    VALUES(?,?,?,'employee',?)
    """,
    (
        data.name,
        data.email,
        data.password,
        data.manager_id
    ))

    employee_id = cur.lastrowid

    cur.execute("""
    INSERT INTO leave_balance
    (user_id)
    VALUES(?)
    """,
    (employee_id,))

    conn.commit()
    conn.close()

    return {
        "message": "Employee Created"
    }


# =====================================================
# GET MANAGERS
# =====================================================

@app.get("/managers")
def managers():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name
    FROM users
    WHERE role='manager'
    """)

    rows = cur.fetchall()

    conn.close()

    return rows
# =====================================================
# APPLY LEAVE
# =====================================================

@app.post("/apply_leave")
def apply_leave(data: LeaveRequest):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT casual,sick,earned
    FROM leave_balance
    WHERE user_id=?
    """,
    (data.employee_id,)
    )

    balance = cur.fetchone()

    if not balance:

        conn.close()

        return {
            "success": False,
            "message": "Balance record not found"
        }

    leave_type = data.leave_type.lower()

    available = 0

    if leave_type == "casual":
        available = balance[0]

    elif leave_type == "sick":
        available = balance[1]

    elif leave_type == "earned":
        available = balance[2]

    else:

        conn.close()

        return {
            "success": False,
            "message": "Invalid leave type"
        }

    if data.days > available:

        conn.close()

        return {
            "success": False,
            "message": "Insufficient leave balance"
        }

    cur.execute("""
    INSERT INTO leaves
    (
        employee_id,
        leave_type,
        start_date,
        end_date,
        days,
        reason,
        created_at
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        data.employee_id,
        data.leave_type,
        data.start_date,
        data.end_date,
        data.days,
        data.reason,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Leave Applied Successfully"
    }


# =====================================================
# LEAVE BALANCE
# =====================================================

@app.get("/leave_balance/{employee_id}")
def leave_balance(employee_id: int):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT casual,sick,earned
    FROM leave_balance
    WHERE user_id=?
    """,
    (employee_id,)
    )

    row = cur.fetchone()

    conn.close()

    if not row:

        return {
            "casual": 0,
            "sick": 0,
            "earned": 0
        }

    return {

        "casual": row[0],
        "sick": row[1],
        "earned": row[2]
    }


# =====================================================
# EMPLOYEE HISTORY
# =====================================================

@app.get("/leave_history/{employee_id}")
def leave_history(employee_id: int):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT
    id,
    leave_type,
    start_date,
    end_date,
    days,
    reason,
    status,
    created_at

    FROM leaves

    WHERE employee_id=?

    ORDER BY id DESC
    """,
    (employee_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


# =====================================================
# MANAGER REQUESTS
# =====================================================

@app.get("/manager_requests/{manager_id}")
def manager_requests(manager_id: int):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT

    l.id,
    u.name,
    l.leave_type,
    l.start_date,
    l.end_date,
    l.days,
    l.reason,
    l.status

    FROM leaves l

    JOIN users u
    ON l.employee_id=u.id

    WHERE u.manager_id=?

    ORDER BY l.id DESC
    """,
    (manager_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


# =====================================================
# APPROVE LEAVE
# =====================================================

@app.put("/approve/{leave_id}/{manager_id}")
def approve_leave(
        leave_id: int,
        manager_id: int
):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT
    employee_id,
    leave_type,
    days,
    status

    FROM leaves

    WHERE id=?
    """,
    (leave_id,)
    )

    leave = cur.fetchone()

    if not leave:

        conn.close()

        return {
            "success": False,
            "message": "Leave not found"
        }

    employee_id = leave[0]
    leave_type = leave[1].lower()
    days = leave[2]
    status = leave[3]

    if status != "Pending":

        conn.close()

        return {
            "success": False,
            "message": "Already processed"
        }

    if leave_type == "casual":

        cur.execute("""
        UPDATE leave_balance
        SET casual=casual-?
        WHERE user_id=?
        """,
        (
            days,
            employee_id
        ))

    elif leave_type == "sick":

        cur.execute("""
        UPDATE leave_balance
        SET sick=sick-?
        WHERE user_id=?
        """,
        (
            days,
            employee_id
        ))

    elif leave_type == "earned":

        cur.execute("""
        UPDATE leave_balance
        SET earned=earned-?
        WHERE user_id=?
        """,
        (
            days,
            employee_id
        ))

    cur.execute("""
    UPDATE leaves

    SET
    status='Approved',
    approved_by=?

    WHERE id=?
    """,
    (
        manager_id,
        leave_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Leave Approved"
    }


# =====================================================
# REJECT LEAVE
# =====================================================

@app.put("/reject/{leave_id}/{manager_id}")
def reject_leave(
        leave_id: int,
        manager_id: int
):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE leaves

    SET
    status='Rejected',
    approved_by=?

    WHERE id=?
    """,
    (
        manager_id,
        leave_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Leave Rejected"
    }


# =====================================================
# ADMIN STATS
# =====================================================

@app.get("/stats")
def stats():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE role='employee'"
    )
    employees = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE role='manager'"
    )
    managers = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM leaves WHERE status='Pending'"
    )
    pending = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM leaves WHERE status='Approved'"
    )
    approved = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM leaves WHERE status='Rejected'"
    )
    rejected = cur.fetchone()[0]

    conn.close()

    return {

        "employees": employees,
        "managers": managers,
        "pending": pending,
        "approved": approved,
        "rejected": rejected
    }


# =====================================================
# ALL USERS
# =====================================================

@app.get("/users")
def users():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT
    id,
    name,
    email,
    role,
    manager_id

    FROM users

    ORDER BY role
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


# =====================================================
# ALL LEAVES
# =====================================================

@app.get("/all_leaves")
def all_leaves():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT

    l.id,
    u.name,
    l.leave_type,
    l.start_date,
    l.end_date,
    l.days,
    l.status

    FROM leaves l

    JOIN users u
    ON l.employee_id=u.id

    ORDER BY l.id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Employee Leave Management API Running"
    }
    