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
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Wipe demo accounts without recreating them.",
        )

    def handle(self, *args, **options):
        demo_users = User.objects.filter(username__startswith="demo-")

        # Delete child rows before parents, before finally deleting the demo
        # Users — every FK below is PROTECT, not CASCADE.
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
            self.stdout.write(self.style.WARNING("Demo accounts cleared. Nothing created."))
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

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(admins)} admins, {len(members)} members.")
        )

        admin_user = admins[0]

        # Category and Tag have no owner FK, so they're never deleted above —
        # get_or_create keeps them idempotent without touching real org data
        # that happens to share a demo category/tag name.
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

        self.stdout.write(self.style.SUCCESS(f"Created {len(DOCUMENTS_DATA)} documents."))

    def _seed_meetings(self, admin_user):
        now = timezone.now()
        meetings_data = [
            {
                "title": "Q3 Planning Session",
                "description": "Plan goals and priorities for Q3.",
                "scheduled_at": now + timedelta(days=5),
                "status": "SCHEDULED",
            },
            {
                "title": "Annual General Meeting",
                "description": "Yearly all-member meeting.",
                "scheduled_at": now + timedelta(days=20),
                "status": "SCHEDULED",
            },
            {
                "title": "Q2 Review",
                "description": "Review of Q2 progress and finances.",
                "scheduled_at": now - timedelta(days=30),
                "status": "COMPLETED",
                "minutes": (
                    "Reviewed Q2 budget vs. actuals, approved the hosting cost "
                    "increase, and agreed to revisit membership dues next quarter."
                ),
            },
            {
                "title": "Budget Workshop",
                "description": "Working session on next year's budget.",
                "scheduled_at": now - timedelta(days=10),
                "status": "CANCELLED",
            },
        ]
        for data in meetings_data:
            Meeting.objects.create(created_by=admin_user, **data)

        self.stdout.write(self.style.SUCCESS(f"Created {len(meetings_data)} meetings."))

    def _seed_finance(self, admin_user, income_categories, expense_categories):
        now = timezone.now().date()
        income_items = [
            (Decimal("2500.00"), "Quarterly grant disbursement"),
            (Decimal("1200.00"), "Membership dues batch"),
            (Decimal("3000.00"), "Annual grant"),
            (Decimal("900.00"), "Membership dues batch"),
            (Decimal("1500.00"), "Sponsorship contribution"),
            (Decimal("600.00"), "Membership dues batch"),
        ]
        expense_items = [
            (Decimal("150.00"), "Monthly server hosting"),
            (Decimal("45.00"), "Design software subscription"),
            (Decimal("300.00"), "Community meetup costs"),
            (Decimal("150.00"), "Monthly server hosting"),
            (Decimal("60.00"), "Email service subscription"),
            (Decimal("150.00"), "Monthly server hosting"),
            (Decimal("220.00"), "Workshop supplies"),
            (Decimal("45.00"), "Design software subscription"),
            (Decimal("400.00"), "Annual conference costs"),
        ]

        count = 0
        for i, (amount, description) in enumerate(income_items):
            category = income_categories[i % len(income_categories)]
            Transaction.objects.create(
                amount=amount,
                transaction_date=now - timedelta(days=(i * 90) // max(len(income_items) - 1, 1)),
                type="INCOME",
                category=category,
                description=description,
                recorded_by=admin_user,
            )
            count += 1

        for i, (amount, description) in enumerate(expense_items):
            category = expense_categories[i % len(expense_categories)]
            Transaction.objects.create(
                amount=amount,
                transaction_date=now - timedelta(days=(i * 90) // max(len(expense_items) - 1, 1)),
                type="EXPENSE",
                category=category,
                description=description,
                recorded_by=admin_user,
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {count} transactions."))

    def _seed_voting(self, admin_user, members):
        now = timezone.now()

        open_ballot = Ballot.objects.create(
            title="Community Event Budget Allocation",
            description="How should we allocate this year's community event budget?",
            opens_at=now - timedelta(days=1),
            closes_at=now + timedelta(days=7),
            created_by=admin_user,
            is_active=True,
        )
        open_options = [
            BallotOption.objects.create(ballot=open_ballot, text=text, display_order=i)
            for i, text in enumerate(
                ["Outdoor Festival", "Virtual Conference", "Hybrid Meetup"]
            )
        ]
        for i, voter in enumerate(members[:4]):
            Vote.objects.create(
                ballot=open_ballot,
                option=open_options[i % len(open_options)],
                voter=voter,
            )

        closed_ballot = Ballot.objects.create(
            title="2026 Board Member Election",
            description="Vote for the new board members for the 2026 term.",
            opens_at=now - timedelta(days=21),
            closes_at=now - timedelta(days=1),
            created_by=admin_user,
            is_active=True,
        )
        closed_options = [
            BallotOption.objects.create(ballot=closed_ballot, text=text, display_order=i)
            for i, text in enumerate(["Candidate A", "Candidate B", "Candidate C"])
        ]
        for i, voter in enumerate(members):
            Vote.objects.create(
                ballot=closed_ballot,
                option=closed_options[i % len(closed_options)],
                voter=voter,
            )

        self.stdout.write(self.style.SUCCESS("Created 2 ballots (1 open, 1 closed) with votes."))

    def _seed_whatsapp(self, admin_user):
        with open(SAMPLE_CHAT_ANALYSIS_PATH) as fh:
            results = json.load(fh)

        with open(SAMPLE_CHAT_EXPORT_PATH, "rb") as fh:
            chat_export = ChatExport.objects.create(
                file=File(fh, name="whatsapp_sample.txt"),
                uploaded_by=admin_user,
                source_group_name="Org X General Chat",
                message_count=results["summary"]["total_messages"],
            )

        ChatAnalysis.objects.create(chat_export=chat_export, results=results)

        self.stdout.write(self.style.SUCCESS("Created 1 WhatsApp chat export with analysis."))
