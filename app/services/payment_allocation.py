from app.domain.payment import PaymentData
from app.models.payment_models import SplitMethod


def validate_split_method_requirements(cursor, data: PaymentData):
    placeholders = ",".join(["?"] * len(data.participant_ids))

    cursor.execute(f"""
        SELECT id, name, average_income
        FROM people
        WHERE id IN ({placeholders})
        ORDER BY id
    """, tuple(data.participant_ids))
    people = cursor.fetchall()

    if len(people) != len(set(data.participant_ids)):
        raise ValueError("One or more participant_ids do not exist.")

    if data.split_method == SplitMethod.income_ratio:
        missing_income = [person["name"] for person in people if person["average_income"] is None]
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


def create_payment_allocations(cursor, payment_id: int, data: PaymentData):
    placeholders = ",".join(["?"] * len(data.participant_ids))

    cursor.execute(f"""
        SELECT id, name, average_income
        FROM people
        WHERE id IN ({placeholders})
        ORDER BY id
    """, tuple(data.participant_ids))
    people = cursor.fetchall()

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