import sqlite3
from app.db.database import get_connection
from app.domain.account import AccountData


def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, person_id, name, account_type, balance, updated_at
            FROM accounts
            ORDER BY name
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch accounts: {str(e)}"
        }

    finally:
        conn.close()


def get_total_balance():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COALESCE(SUM(balance), 0) AS total_balance
            FROM accounts
        """)
        row = cursor.fetchone()
        return row["total_balance"]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to calculate total balance: {str(e)}"
        }

    finally:
        conn.close()


def create_account(data: AccountData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO accounts (person_id, name, account_type, balance, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.person_id,
            data.name,
            data.account_type.value,
            data.balance,
            data.updated_at
        ))

        conn.commit()

        return {
            "status": "ok",
            "id": cursor.lastrowid
        }

    except sqlite3.IntegrityError as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Integrity error: {str(e)}"
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to create account: {str(e)}"
        }

    finally:
        conn.close()


def update_account(account_id: int, data: AccountData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM accounts WHERE id = ?
        """, (account_id,))
        row = cursor.fetchone()

        if row is None:
            return {"status": "error", "message": "Account not found"}

        cursor.execute("""
            UPDATE accounts
            SET person_id = ?, name = ?, account_type = ?, balance = ?, updated_at = ?
            WHERE id = ?
        """, (
            data.person_id,
            data.name,
            data.account_type.value,
            data.balance,
            data.updated_at,
            account_id
        ))

        conn.commit()

        return {
            "status": "ok",
            "updated_id": account_id
        }

    except sqlite3.IntegrityError as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Integrity error: {str(e)}"
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to update account: {str(e)}"
        }

    finally:
        conn.close()


def delete_account(account_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM accounts WHERE id = ?
        """, (account_id,))
        row = cursor.fetchone()

        if row is None:
            return {"status": "error", "message": "Account not found"}

        cursor.execute("""
            DELETE FROM accounts WHERE id = ?
        """, (account_id,))

        conn.commit()

        return {
            "status": "ok",
            "deleted_id": account_id
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to delete account: {str(e)}"
        }

    finally:
        conn.close()