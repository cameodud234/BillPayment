from app.db.database import get_connection
from app.domain.account import AccountData


def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, person_id, name, account_type, balance, updated_at, created_at
        FROM accounts
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_account_by_id(account_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, person_id, name, account_type, balance, updated_at, created_at
        FROM accounts
        WHERE id = ?
    """, (account_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


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


def create_account(data: AccountData):
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

    return {
        "status": "ok",
        "id": account_id
    }


def update_account(account_id: int, data: AccountData):
    conn = get_connection()
    cursor = conn.cursor()

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


def delete_account(account_id: int):
    conn = get_connection()
    cursor = conn.cursor()

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