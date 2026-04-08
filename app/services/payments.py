from datetime import date, datetime, timedelta
from app.db.database import get_connection
from app.models import payment_models


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


def create_payment(data: payment_models.AddPaymentRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (name, amount, due_date, category, account_id, is_recurring, due_day)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data.name, data.amount, data.due_date, data.category, data.account_id, data.is_recurring, data.due_day))

    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "id": payment_id
    }


def delete_payment(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # Optional: check if payment exists
    cursor.execute("""
        SELECT id FROM payments WHERE id = ?
    """, (payment_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"status": "error", "message": "Payment not found"}

    # Delete payment (allocations will auto-delete if ON DELETE CASCADE is set)
    cursor.execute("""
        DELETE FROM payments WHERE id = ?
    """, (payment_id,))

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "deleted_id": payment_id
    }


def get_weekly_budget(data: payment_models.WeeklyBudgetRequest):
    payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
    end = payday + timedelta(days=6)

    filtered = get_payments_due_between(payday, end)
    total = sum(item["amount"] for item in filtered)

    return {
        "total": total,
        "payments": filtered
    }