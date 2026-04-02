import sqlite3
from app.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # PEOPLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        payday TEXT,
        pay_schedule TEXT,
        anchor_date TEXT,
        average_income REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ACCOUNTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        name TEXT NOT NULL,
        type TEXT,
        balance REAL DEFAULT 0,
        updated_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE SET NULL
    )
    """)

    # PAYMENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        category TEXT,
        is_recurring INTEGER DEFAULT 0,
        due_day INTEGER,
        account_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE SET NULL
    )
    """)

    conn.commit()
    conn.close()