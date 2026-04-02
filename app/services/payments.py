from datetime import date, datetime, timedelta
from app.db.database import get_connection


def get_all_payments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, due_date, category, account_id
        FROM payments
        ORDER BY due_date
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_payments_due_between(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, due_date, category, account_id, is_recurring, due_day, created_at
        FROM payments
        WHERE due_date BETWEEN ? AND ?
        ORDER BY due_date
    """, (start_date.isoformat(), end_date.isoformat()))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_payment(
    name: str,
    amount: float,
    due_date: str,
    category: str,
    account_id: int | None = None,
    is_recurring: int = 0,
    due_day: int | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (name, amount, due_date, category, account_id, is_recurring, due_day)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, amount, due_date, category, account_id, is_recurring, due_day))

    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "id": payment_id
    }

def get_weekly_budget(payday_str: str):
    payday = datetime.strptime(payday_str, "%Y-%m-%d").date()
    end = payday + timedelta(days=6)

    filtered = get_payments_due_between(payday, end)
    total = sum(item["amount"] for item in filtered)

    return {
        "total": total,
        "payments": filtered
    }