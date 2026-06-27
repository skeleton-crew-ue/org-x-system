from django.core.management.base import BaseCommand
from django.utils import timezone
from members.models import User
from meetings.models import Meeting
from finance.models import Transaction, Category

ADMIN_NAMES = [
    ("Alice", "Nguyen"),
    ("Bob", "Okafor"),
    ("Carol", "Martinez"),
]

MEMBER_NAMES = [
    ("David", "Kim"),
    ("Eva", "Patel"),
    ("Frank", "Osei"),
    ("Grace", "Lindqvist"),
    ("Henry", "Adeyemi"),
    ("Iris", "Johansson"),
    ("James", "Castillo"),
    ("Karen", "Mwangi"),
    ("Liam", "Schneider"),
    ("Maya", "Tanaka"),
    ("Nour", "Hassan"),
    ("Omar", "Ferreira"),
]

PASSWORD = "demo1234"

class Command(BaseCommand):
    help = "Reset and re-create the demo dataset (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Wipe demo accounts.")

    def handle(self, *args, **options):
        # 1. Limpieza total de los módulos
        Transaction.objects.all().delete()
        Category.objects.all().delete()
        Meeting.objects.all().delete()
        deleted, _ = User.objects.filter(username__startswith="demo-").delete()
        
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Demo data cleared."))
            return

        # 2. Creación de usuarios
        for i, (first, last) in enumerate(ADMIN_NAMES, start=1):
            User.objects.create_user(
                username=f"demo-admin-{i}",
                email=f"demo-admin-{i}@example.com",
                password=PASSWORD,
                first_name=first,
                last_name=last,
                role=User.Role.ADMIN,
                is_staff=True,
            )
        
        admin_user = User.objects.filter(role=User.Role.ADMIN).first()

        # 3. Creación de datos para Meetings
        if admin_user:
            meetings_data = [
                {"title": "Sprint Planning", "description": "Discussing goals", "scheduled_at": timezone.now(), "created_by": admin_user},
                {"title": "Review", "description": "Q2 review", "scheduled_at": timezone.now(), "created_by": admin_user, "status": "COMPLETED"},
            ]
            for m in meetings_data:
                Meeting.objects.create(**m)

        # 4. Creación de datos para Finance
        if admin_user:
            cat_income = Category.objects.create(name="Grant", type="INCOME")
            cat_expense = Category.objects.create(name="Hosting", type="EXPENSE")
            
            transactions_data = [
                {"amount": 2500.00, "transaction_date": timezone.now().date(), "type": "INCOME", "category": cat_income, "description": "Organization X Grant", "recorded_by": admin_user},
                {"amount": 150.00, "transaction_date": timezone.now().date(), "type": "EXPENSE", "category": cat_expense, "description": "Server Costs", "recorded_by": admin_user},
            ]
            for t in transactions_data:
                Transaction.objects.create(**t)

        self.stdout.write(self.style.SUCCESS("Demo data for Users, Meetings, and Finance successfully created!"))