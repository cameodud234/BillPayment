from app.domain.payment import PaymentData
from app.models.payment_models import SplitMethod

def validate_split_method_requirements(cursor, data: PaymentData):
    if data.split_method == data.split_method.income_ratio:
        cursor.execute("""
            SELECT id, name, average_income
            FROM people
            ORDER BY id
        """)
        people = cursor.fetchall()

        if not people:
            raise ValueError("Cannot use income_ratio split: no people exist.")

        missing_income = [person["name"] for person in people if person["average_income"] is None]

        if missing_income:
            names = ", ".join(missing_income)
            raise ValueError(
                f"Cannot use income_ratio split: missing average_income for {names}."
            )

        total_income = sum(person["average_income"] for person in people)

        if total_income <= 0:
            raise ValueError("Cannot use income_ratio split: total average_income must be greater than 0.")

    elif data.split_method == data.split_method.equal:
        cursor.execute("SELECT COUNT(*) AS count FROM people")
        row = cursor.fetchone()

        if row["count"] < 2:
            raise ValueError("Cannot use equal split: at least 2 people are required.")

    elif data.split_method == data.split_method.single:
        if data.single_person_id is None:
            raise ValueError("single_person_id is required for single split.")

        cursor.execute("""
            SELECT id FROM people WHERE id = ?
        """, (data.single_person_id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError("single_person_id does not exist.")
        

def create_payment_allocations(cursor, payment_id: int, data: PaymentData):
    if data.split_method == SplitMethod.single:
        cursor.execute("""
            INSERT INTO payment_allocations (payment_id, person_id, share_percentage, allocated_amount)
            VALUES (?, ?, ?, ?)
        """, (payment_id, data.single_person_id, 100.0, data.amount))
        return

    cursor.execute("""
        SELECT id, name, average_income
        FROM people
        ORDER BY id
    """)
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
                INSERT INTO payment_allocations (payment_id, person_id, share_percentage, allocated_amount)
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
                INSERT INTO payment_allocations (payment_id, person_id, share_percentage, allocated_amount)
                VALUES (?, ?, ?, ?)
            """, (payment_id, person["id"], share, allocated))