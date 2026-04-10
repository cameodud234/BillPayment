from app.db.database import get_connection
from app.domain.person import PersonData


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


def get_person_by_id(person_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, payday, pay_schedule, anchor_date, average_income
        FROM people
        WHERE id = ?
    """, (person_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


def create_person(data: PersonData):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO people (name, pay_schedule, payday, anchor_date, average_income)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.name,
        data.pay_schedule,
        data.payday,
        data.anchor_date,
        data.average_income
    ))

    conn.commit()
    person_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "id": person_id
    }


def update_person(person_id: int, data: PersonData):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM people WHERE id = ?
    """, (person_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"status": "error", "message": "Person not found"}

    cursor.execute("""
        UPDATE people
        SET name = ?, payday = ?, pay_schedule = ?, anchor_date = ?, average_income = ?
        WHERE id = ?
    """, (
        data.name,
        data.payday,
        data.pay_schedule,
        data.anchor_date,
        data.average_income,
        person_id
    ))

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "updated_id": person_id
    }


def delete_person(person_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM people WHERE id = ?
    """, (person_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"status": "error", "message": "Person not found"}

    cursor.execute("""
        DELETE FROM people WHERE id = ?
    """, (person_id,))

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "deleted_id": person_id
    }