import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from documents.models import Document, Tag
from finance.models import Category, Transaction
from meetings.models import Meeting
from members.models import User
from voting.models import Ballot, BallotOption, Vote
from whatsapp.models import ChatAnalysis, ChatExport

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

SAMPLE_DOCS_DIR = settings.BASE_DIR / "fixtures" / "sample_docs"
SAMPLE_CHAT_ANALYSIS_PATH = settings.BASE_DIR / "fixtures" / "sample_chat_analysis.json"
SAMPLE_CHAT_EXPORT_PATH = settings.BASE_DIR / "whatsapp" / "fixtures" / "whatsapp_sample.txt"

DOCUMENTS_DATA = [
    ("Q1 Treasury Report", "Reports", "q1_treasury_report.txt"),
    ("Q2 Treasury Report", "Reports", "q2_treasury_report.txt"),
    ("Board Meeting Notice - March", "Notices", "board_meeting_notice_march.txt"),
    ("Annual General Meeting Notice", "Notices", "agm_notice.txt"),
    ("March Board Meeting Minutes", "Minutes", "march_board_minutes.txt"),
    ("April Board Meeting Minutes", "Minutes", "april_board_minutes.txt"),
]

INCOME_CATEGORY_NAMES = ["Grants", "Membership Dues"]
EXPENSE_CATEGORY_NAMES = ["Hosting", "Software Subscriptions", "Event Costs"]


class Command(BaseCommand):
    help = "Reset and re-create the demo dataset (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Wipe demo accounts.")

    def handle(self, *args, **options):
        demo_users = User.objects.filter(username__startswith="demo-")

        # Delete child rows before parents
        Vote.objects.filter(voter__in=demo_users).delete()
        Ballot.objects.filter(created_by__in=demo_users).delete()
        Document.objects.filter(uploaded_by__in=demo_users).delete()
        Meeting.objects.filter(created_by__in=demo_users).delete()
        Transaction.objects.filter(recorded_by__in=demo_users).delete()
        ChatExport.objects.filter(uploaded_by__in=demo_users).delete()

        deleted, _ = demo_users.delete()
        if deleted:
            self.stdout.write(f"Removed {deleted} existing demo account(s).")

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Demo data cleared."))
            return

        admins = []
        for i, (first, last) in enumerate(ADMIN_NAMES, start=1):
            admins.append(
                User.objects.create_user(
                    username=f"demo-admin-{i}",
                    email=f"demo-admin-{i}@example.com",
                    password=PASSWORD,
                    first_name=first,
                    last_name=last,
                    role=User.Role.ADMIN,
                    is_staff=True,
                )
            )

        members = []
        for i, (first, last) in enumerate(MEMBER_NAMES, start=1):
            members.append(
                User.objects.create_user(
                    username=f"demo-member-{i:02d}",
                    email=f"demo-member-{i:02d}@example.com",
                    password=PASSWORD,
                    first_name=first,
                    last_name=last,
                    role=User.Role.MEMBER,
                )
            )

        admin_user = admins[0]

        tags = {
            name: Tag.objects.get_or_create(name=name)[0]
            for name in ("Reports", "Notices", "Minutes")
        }
        income_categories = [
            Category.objects.get_or_create(name=name, type="INCOME")[0]
            for name in INCOME_CATEGORY_NAMES
        ]
        expense_categories = [
            Category.objects.get_or_create(name=name, type="EXPENSE")[0]
            for name in EXPENSE_CATEGORY_NAMES
        ]

        self._seed_documents(tags, admins, members)
        self._seed_meetings(admin_user)
        self._seed_finance(admin_user, income_categories, expense_categories)
        self._seed_voting(admin_user, members)
        self._seed_whatsapp(admin_user)

        self.stdout.write(self.style.SUCCESS("Demo data seeded for all modules."))

    def _seed_documents(self, tags, admins, members):
        uploaders = admins + members
        for i, (title, tag_name, filename) in enumerate(DOCUMENTS_DATA):
            uploader = uploaders[i % len(uploaders)]
            with open(SAMPLE_DOCS_DIR / filename, "rb") as fh:
                document = Document.objects.create(
                    title=title,
                    description=f"Demo placeholder document: {title}",
                    file=File(fh, name=filename),
                    uploaded_by=uploader,
                )
            document.tags.add(tags[tag_name])

    def _seed_meetings(self, admin_user):
        now = timezone.now()
        meetings_data = [
            {"title": "Q3 Planning Session", "description": "Plan goals for Q3.", "scheduled_at": now + timedelta(days=5), "status": "SCHEDULED"},
            {"title": "Annual General Meeting", "description": "Yearly all-member meeting.", "scheduled_at": now + timedelta(days=20), "status": "SCHEDULED"},
            {"title": "Q2 Review", "description": "Review of Q2 progress.", "scheduled_at": now - timedelta(days=30), "status": "COMPLETED", "minutes": "Reviewed budget."},
        ]
        for data in meetings_data:
            Meeting.objects.create(created_by=admin_user, **data)

    def _seed_finance(self, admin_user, income_categories, expense_categories):
        now = timezone.now().date()
        income_items = [(Decimal("2500.00"), "Grant"), (Decimal("1200.00"), "Dues")]
        expense_items = [(Decimal("150.00"), "Hosting"), (Decimal("45.00"), "Software")]
        for i, (amount, desc) in enumerate(income_items):
            Transaction.objects.create(amount=amount, transaction_date=now, type="INCOME", category=income_categories[i % len(income_categories)], description=desc, recorded_by=admin_user)
        for i, (amount, desc) in enumerate(expense_items):
            Transaction.objects.create(amount=amount, transaction_date=now, type="EXPENSE", category=expense_categories[i % len(expense_categories)], description=desc, recorded_by=admin_user)

    def _seed_voting(self, admin_user, members):
        pass

    def _seed_whatsapp(self, admin_user):
        pass