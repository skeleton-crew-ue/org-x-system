import csv
import random
from datetime import datetime, timedelta

from faker import Faker


fake = Faker()
random.seed(42)
Faker.seed(42)

TOTAL_ROWS = 4000
OUTPUT_FILE = "fixtures/members_4k.csv"
FIELDNAMES = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "member_id",
    "joined_at",
]
def generate_member_id():
    if random.random() < 0.02:
        return f"OX-{random.randint(1000, 9999)}"

    return f"M-{random.randint(100000, 999999)}"

def generate_joined_at():
    start_date = datetime(2018, 1, 1)
    end_date = datetime.now()

    random_days = random.randint(
        0,
        (end_date - start_date).days
    )

    joined_at = start_date + timedelta(days=random_days)

    return joined_at.strftime("%Y-%m-%d")

def generate_rows():
        rows = []

        for i in range(TOTAL_ROWS):
            first_name = fake.first_name()
            last_name = fake.last_name()

            rows.append({
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{first_name}.{last_name}.{i}@example.com".lower(),
                "phone": fake.phone_number(),
                "member_id": generate_member_id(),
                "joined_at": generate_joined_at(),
            })

        return rows
def write_csv(rows):
        with open(OUTPUT_FILE, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
if __name__ == "__main__":
    rows = generate_rows()
    write_csv(rows)
    print(f"Created {OUTPUT_FILE} with {len(rows)} rows")