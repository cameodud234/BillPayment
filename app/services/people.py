from app.db.database import get_connection


def get_all_people():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, pay_schedule, payday, anchor_date, average_income, created_at
        FROM people
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_person(
    name: str,
    pay_schedule: str,
    payday: str,
    anchor_date: str | None = None,
    average_income: float | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO people (name, pay_schedule, payday, anchor_date, average_income)
        VALUES (?, ?, ?, ?, ?)
    """, (name, pay_schedule, payday, anchor_date, average_income))

    conn.commit()
    person_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "id": person_id
    }