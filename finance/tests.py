from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from members.models import User
from .models import Category, Transaction


class FinanceSummaryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="x", role=User.Role.ADMIN)
        self.income_category = Category.objects.create(name="Dues", type="INCOME")
        self.expense_category = Category.objects.create(name="Venue", type="EXPENSE")
        self.client.force_login(self.admin)

    def test_aggregates_match_expected(self):
        Transaction.objects.create(
            amount=Decimal("100.00"), transaction_date="2026-07-01", type="INCOME",
            category=self.income_category, recorded_by=self.admin,
        )
        Transaction.objects.create(
            amount=Decimal("50.00"), transaction_date="2026-07-02", type="INCOME",
            category=self.income_category, recorded_by=self.admin,
        )
        Transaction.objects.create(
            amount=Decimal("30.00"), transaction_date="2026-07-03", type="EXPENSE",
            category=self.expense_category, recorded_by=self.admin,
        )

        response = self.client.get(reverse("finance:summary"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["income_total"], Decimal("150.00"))
        self.assertEqual(response.context["expense_total"], Decimal("30.00"))
        self.assertEqual(response.context["net_balance"], Decimal("120.00"))

    def test_empty_state_does_not_500(self):
        response = self.client.get(reverse("finance:summary"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["income_total"], 0)
        self.assertEqual(response.context["expense_total"], 0)
        self.assertEqual(response.context["net_balance"], 0)
