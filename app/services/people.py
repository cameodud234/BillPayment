import sqlite3

from app.db.database import get_connection
from app.domain.person import PersonData


def get_all_people():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, pay_schedule, payday, anchor_date, average_income, created_at
            FROM people
            ORDER BY name
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch people: {str(e)}"
        }

    finally:
        conn.close()


def get_person_by_id(person_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, payday, pay_schedule, anchor_date, average_income
            FROM people
            WHERE id = ?
        """, (person_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch person: {str(e)}"
        }

    finally:
        conn.close()


def create_person(data: PersonData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO people (
                name,
                pay_schedule,
                payday,
                anchor_date,
                average_income
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.name,
            data.pay_schedule,
            data.payday,
            data.anchor_date,
            data.average_income
        ))

        conn.commit()

        return {
            "status": "ok",
            "id": cursor.lastrowid
        }

    except sqlite3.IntegrityError:
        conn.rollback()
        return {
            "status": "error",
            "message": "Person with this name already exists"
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to create person: {str(e)}"
        }

    finally:
        conn.close()


def update_person(person_id: int, data: PersonData):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM people WHERE id = ?
        """, (person_id,))
        row = cursor.fetchone()

        if row is None:
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

        return {
            "status": "ok",
            "updated_id": person_id
        }

    except sqlite3.IntegrityError:
        conn.rollback()
        return {
            "status": "error",
            "message": "Person with this name already exists"
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to update person: {str(e)}"
        }

    finally:
        conn.close()


def delete_person(person_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM people WHERE id = ?
        """, (person_id,))
        row = cursor.fetchone()

        if row is None:
            return {"status": "error", "message": "Person not found"}

        cursor.execute("""
            DELETE FROM people WHERE id = ?
        """, (person_id,))

        conn.commit()

        return {
            "status": "ok",
            "deleted_id": person_id
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Failed to delete person: {str(e)}"
        }

    finally:
        conn.close()