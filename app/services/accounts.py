from app.db.database import get_connection
from app.models import account_models


def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, person_id, name, account_type, balance, updated_at
        FROM accounts
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_total_balance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(balance), 0) AS total_balance
        FROM accounts
    """)

    row = cursor.fetchone()
    conn.close()

    return row["total_balance"]


def create_account(data: account_models.AddAccountRequest):
    conn = get_connection()
    cursor = conn.cursor()

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
    account_id = cursor.lastrowid
    conn.close()

    return {"status": "ok", "id": account_id}


# 🔧 UPDATE
def update_account(account_id: int, data: account_models.UpdateAccountRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Check existence
    cursor.execute("""
        SELECT id FROM accounts WHERE id = ?
    """, (account_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
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
    conn.close()

    return {
        "status": "ok",
        "updated_id": account_id
    }


# 🗑 DELETE
def delete_account(account_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # Check existence
    cursor.execute("""
        SELECT id FROM accounts WHERE id = ?
    """, (account_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"status": "error", "message": "Account not found"}

    cursor.execute("""
        DELETE FROM accounts WHERE id = ?
    """, (account_id,))

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "deleted_id": account_id
    }