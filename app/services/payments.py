from datetime import datetime, timedelta
from app.db.database import get_connection
from app.domain.payment import PaymentData, WeeklyBudgetData


def get_all_payments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, due_date, category, account_id, split_method, is_recurring, due_day, created_at
        FROM payments
        ORDER BY due_date
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_payment(data: PaymentData):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (
            name, amount, due_date, category, account_id, split_method, is_recurring, due_day
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.name,
        data.amount,
        data.due_date,
        data.category.value,
        data.account_id,
        data.split_method.value,
        1 if data.is_recurring else 0,
        data.due_day
    ))

    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "id": payment_id
    }


def get_payments_due_between(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, due_date, category, account_id, split_method, is_recurring, due_day, created_at
        FROM payments
        WHERE due_date BETWEEN ? AND ?
        ORDER BY due_date
    """, (start_date.isoformat(), end_date.isoformat()))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_weekly_budget(data: WeeklyBudgetData):
    payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
    end = payday + timedelta(days=6)

    filtered = get_payments_due_between(payday, end)
    total = sum(item["amount"] for item in filtered)

    return {
        "total": total,
        "payments": filtered
    }