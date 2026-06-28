from django.core.management.base import BaseCommand
from members.models import User
from finance.models import Transaction, Category
from meetings.models import Meeting

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
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Wipe demo accounts without recreating them.",
        )

    def handle(self, *args, **options):
        # 1. Identificar usuarios demo antes de borrar registros relacionados
        demo_users = User.objects.filter(username__startswith="demo-")
        demo_admins = demo_users.filter(role=User.Role.ADMIN)

        # 2. Borrado seguro: Solo borramos lo creado por nuestros usuarios de prueba
        Transaction.objects.filter(recorded_by__in=demo_admins).delete()
        Meeting.objects.filter(created_by__in=demo_admins).delete()
        Category.objects.filter(name__in=["Grant", "Hosting"]).delete()

        # 3. Borrar los usuarios demo
        deleted, _ = demo_users.delete()
        if deleted:
            self.stdout.write(f"Removed {deleted} existing demo account(s).")

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Demo accounts cleared. Nothing created."))
            return

        # 4. Crear Administradores
        admins_created = 0
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
            admins_created += 1

        # 5. Crear Miembros (Ahora sí se incluyen)
        members_created = 0
        for i, (first, last) in enumerate(MEMBER_NAMES, start=1):
            User.objects.create_user(
                username=f"demo-member-{i:02d}",
                email=f"demo-member-{i:02d}@example.com",
                password=PASSWORD,
                first_name=first,
                last_name=last,
                role=User.Role.MEMBER,
            )
            members_created += 1

        total = admins_created + members_created
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {admins_created} admins, {members_created} members. Total: {total}."
            )
        )