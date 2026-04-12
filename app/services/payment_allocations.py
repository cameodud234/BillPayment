import sqlite3
from app.db.database import get_connection
from app.domain.payment import PaymentData
from app.models.payment_models import SplitMethod


def get_allocations_by_payment_id(cursor, payment_id: int):
    cursor.execute("""
        SELECT
            id,
            payment_id,
            person_id,
            share_percentage,
            allocated_amount
        FROM payment_allocations
        WHERE payment_id = ?
        ORDER BY person_id
    """, (payment_id,))

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def fetch_allocations_by_payment_id(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        return get_allocations_by_payment_id(cursor, payment_id)

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch allocations: {str(e)}"
        }

    finally:
        conn.close()


def get_payment_allocations(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM payments
            WHERE id = ?
        """, (payment_id,))
        payment = cursor.fetchone()

        if payment is None:
            return {
                "status": "error",
                "message": "Payment not found"
            }

        allocations = get_allocations_by_payment_id(cursor, payment_id)

        return {
            "status": "ok",
            "payment_id": payment_id,
            "allocations": allocations
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get payment allocations: {str(e)}"
        }

    finally:
        conn.close()


def map_allocations_by_person_id(allocations: list[dict]):
    try:
        return {row["person_id"]: row for row in allocations}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to map allocations: {str(e)}"
        }


def sum_allocated_amounts(allocations: list[dict]) -> float:
    try:
        return round(sum(row["allocated_amount"] for row in allocations), 2)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to sum allocated amounts: {str(e)}"
        }


def count_allocations_for_payment(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM payment_allocations
            WHERE payment_id = ?
        """, (payment_id,))
        row = cursor.fetchone()
        return row["count"]

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to count allocations: {str(e)}"
        }

    finally:
        conn.close()


def delete_allocations_for_payment(cursor, payment_id: int):
    try:
        cursor.execute("""
            DELETE FROM payment_allocations
            WHERE payment_id = ?
        """, (payment_id,))
    except Exception as e:
        raise ValueError(f"Failed to delete allocations for payment {payment_id}: {str(e)}")


def _fetch_participants(cursor, participant_ids: list[int]):
    try:
        if not participant_ids:
            raise ValueError("participant_ids must not be empty")

        placeholders = ",".join(["?"] * len(participant_ids))

        cursor.execute(f"""
            SELECT id, name, average_income
            FROM people
            WHERE id IN ({placeholders})
            ORDER BY id
        """, tuple(participant_ids))

        people = cursor.fetchall()

        if len(people) != len(set(participant_ids)):
            raise ValueError("One or more participant_ids do not exist.")

        return people

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to fetch participants: {str(e)}")


def validate_split_method_requirements(cursor, data: PaymentData):
    try:
        people = _fetch_participants(cursor, data.participant_ids)

        if data.split_method == SplitMethod.income_ratio:
            missing_income = [
                person["name"]
                for person in people
                if person["average_income"] is None
            ]

            if missing_income:
                names = ", ".join(missing_income)
                raise ValueError(
                    f"Cannot use income_ratio split: missing average_income for {names}."
                )

            total_income = sum(person["average_income"] for person in people)
            if total_income <= 0:
                raise ValueError(
                    "Cannot use income_ratio split: total average_income must be greater than 0."
                )

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to validate split method requirements: {str(e)}")


def create_payment_allocations(cursor, payment_id: int, data: PaymentData):
    try:
        people = _fetch_participants(cursor, data.participant_ids)

        if len(people) == 1:
            person = people[0]
            cursor.execute("""
                INSERT INTO payment_allocations (
                    payment_id, person_id, share_percentage, allocated_amount
                )
                VALUES (?, ?, ?, ?)
            """, (payment_id, person["id"], 100.0, round(data.amount, 2)))
            return

        if data.split_method == SplitMethod.equal:
            per_person = round(data.amount / len(people), 2)
            running = 0.0

            for i, person in enumerate(people):
                if i == len(people) - 1:
                    allocated = round(data.amount - running, 2)
                else:
                    allocated = per_person
                    running += allocated

                share = round((allocated / data.amount) * 100, 2)

                cursor.execute("""
                    INSERT INTO payment_allocations (
                        payment_id, person_id, share_percentage, allocated_amount
                    )
                    VALUES (?, ?, ?, ?)
                """, (payment_id, person["id"], share, allocated))

        elif data.split_method == SplitMethod.income_ratio:
            total_income = sum(person["average_income"] for person in people)
            running = 0.0

            for i, person in enumerate(people):
                ratio = person["average_income"] / total_income

                if i == len(people) - 1:
                    allocated = round(data.amount - running, 2)
                else:
                    allocated = round(data.amount * ratio, 2)
                    running += allocated

                share = round(ratio * 100, 2)

                cursor.execute("""
                    INSERT INTO payment_allocations (
                        payment_id, person_id, share_percentage, allocated_amount
                    )
                    VALUES (?, ?, ?, ?)
                """, (payment_id, person["id"], share, allocated))

        else:
            raise ValueError(f"Unsupported split_method: {data.split_method}")

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to create payment allocations: {str(e)}")