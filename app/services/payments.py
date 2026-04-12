from datetime import datetime, timedelta
from app.db.database import get_connection
from app.domain.payment import PaymentData, WeeklyBudgetData
from app.services import payment_allocations


def get_all_payments():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                id,
                name,
                amount,
                due_date,
                category,
                account_id,
                split_method,
                is_recurring,
                due_day,
                created_at
            FROM payments
            ORDER BY due_date
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch payments: {str(e)}"
        }

    finally:
        conn.close()


def get_payment_by_id(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                id,
                name,
                amount,
                due_date,
                category,
                account_id,
                split_method,
                is_recurring,
                due_day,
                created_at
            FROM payments
            WHERE id = ?
        """, (payment_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch payment: {str(e)}"
        }

    finally:
        conn.close()


def get_payments_due_between(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                id,
                name,
                amount,
                due_date,
                category,
                account_id,
                split_method,
                is_recurring,
                due_day,
                created_at
            FROM payments
            WHERE due_date BETWEEN ? AND ?
            ORDER BY due_date
        """, (start_date.isoformat(), end_date.isoformat()))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch payments in range: {str(e)}"
        }

    finally:
        conn.close()


def create_payment(data: PaymentData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        payment_allocations.validate_split_method_requirements(cursor, data)

        cursor.execute("""
            INSERT INTO payments (
                name,
                amount,
                due_date,
                category,
                account_id,
                split_method,
                is_recurring,
                due_day
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

        payment_id = cursor.lastrowid

        payment_allocations.create_payment_allocations(cursor, payment_id, data)

        conn.commit()
        return {
            "status": "ok",
            "id": payment_id
        }

    except ValueError as e:
        conn.rollback()
        return {
            "status": "error",
            "message": str(e)
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to create payment: {str(e)}"
        }

    finally:
        conn.close()


def update_payment(payment_id: int, data: PaymentData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM payments
            WHERE id = ?
        """, (payment_id,))
        row = cursor.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": "Payment not found"
            }

        payment_allocations.validate_split_method_requirements(cursor, data)

        cursor.execute("""
            UPDATE payments
            SET
                name = ?,
                amount = ?,
                due_date = ?,
                category = ?,
                account_id = ?,
                split_method = ?,
                is_recurring = ?,
                due_day = ?
            WHERE id = ?
        """, (
            data.name,
            data.amount,
            data.due_date,
            data.category.value,
            data.account_id,
            data.split_method.value,
            1 if data.is_recurring else 0,
            data.due_day,
            payment_id
        ))

        payment_allocations.delete_allocations_for_payment(cursor, payment_id)
        payment_allocations.create_payment_allocations(cursor, payment_id, data)

        conn.commit()

        return {
            "status": "ok",
            "updated_id": payment_id
        }

    except ValueError as e:
        conn.rollback()
        return {
            "status": "error",
            "message": str(e)
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to update payment: {str(e)}"
        }

    finally:
        conn.close()


def delete_payment(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM payments
            WHERE id = ?
        """, (payment_id,))
        row = cursor.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": "Payment not found"
            }

        cursor.execute("""
            DELETE FROM payments
            WHERE id = ?
        """, (payment_id,))

        conn.commit()

        return {
            "status": "ok",
            "deleted_id": payment_id
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to delete payment: {str(e)}"
        }

    finally:
        conn.close()


def get_weekly_budget(data: WeeklyBudgetData):
    try:
        payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
        end = payday + timedelta(days=6)

        filtered = get_payments_due_between(payday, end)

        if isinstance(filtered, dict) and filtered.get("status") == "error":
            return filtered

        total = sum(item["amount"] for item in filtered)

        return {
            "status": "ok",
            "total": total,
            "payments": filtered
        }

    except ValueError:
        return {
            "status": "error",
            "message": "payday must be YYYY-MM-DD"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to calculate weekly budget: {str(e)}"
        }