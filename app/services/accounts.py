from app.db.database import get_connection


def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, person_id, name, type, balance, updated_at
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


def create_account(person_id, name: str, account_type: str, balance: float, updated_at: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO accounts (person_id, name, type, balance, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (person_id, name, account_type, balance, updated_at))

    conn.commit()
    account_id = cursor.lastrowid
    conn.close()

    return {"status": "ok", "id": account_id}