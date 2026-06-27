import csv
import random
from datetime import date, timedelta

OUTPUT_FILE = "org-x-system/fixtures/members_4k.csv"

FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David",
    "Emma", "Chris", "Olivia", "Daniel", "Sophia",
    "Robert", "Emily", "James", "Anna"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown",
    "Jones", "Miller", "Davis", "Wilson",
    "Taylor", "Anderson"
]

def random_date():
    start = date(2015, 1, 1)
    end = date(2025, 1, 1)

    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "email",
        "first_name",
        "last_name",
        "phone",
        "member_id",
        "joined_at"
    ])

    for i in range(4000):

        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        email = f"{first.lower()}.{last.lower()}{i}@example.org"

        phone = f"5{random.randint(10000000,99999999)}"

        member_id = f"M-{i+1:06d}"

        joined_at = random_date()

        writer.writerow([
            email,
            first,
            last,
            phone,
            member_id,
            joined_at
        ])

    # Dirty rows for testing cleaning rules

    writer.writerow([
        "",
        "Blank",
        "Email",
        "555111111",
        "M-999991",
        "2024-01-01"
    ])

    writer.writerow([
        "invalid-email",
        "Bad",
        "Email",
        "555222222",
        "M-999992",
        "2024-01-01"
    ])

    writer.writerow([
        "john.smith0@example.org",
        "Duplicate",
        "User",
        "(555)-123-456",
        "",
        "March 2023"
    ])

print("Generated 4000+ member records")
print("Saved to:", OUTPUT_FILE)