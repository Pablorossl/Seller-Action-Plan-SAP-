from datetime import date
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from quality.models import QualityMetric, ThresholdPolicy
from quality.services import classify
from sellers.management.commands.seed_demo import POLICIES
from sellers.models import Seller


class QualityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="owner")
        cls.seller = Seller.objects.create(name="Ficticia", reference="TEST", owner=cls.user)
        cls.policies = {}
        for code, unit, operator, alarm, suspension, mqc in POLICIES:
            cls.policies[code] = ThresholdPolicy.objects.create(
                code=code, unit=unit, operator=operator, alarm=Decimal(alarm),
                suspension=Decimal(suspension) if suspension else None, is_mqc=mqc,
                minimum_orders=30 if mqc else 0,
            )

    def metric(self, code, value, orders=30, **kwargs):
        return QualityMetric(seller=self.seller, policy=self.policies[code],
            channel="test-es", period_start=date(2026, 9, 1), period_end=date(2026, 9, 30),
            order_count=orders, value=Decimal(value), **kwargs)

    def test_all_exact_mqc_boundaries(self):
        cases = {
            "acceptance": [("99", "ok"), ("98.99", "alarm"), ("98", "alarm"), ("97.99", "suspension_threshold")],
            "incidents": [("3.99", "ok"), ("4", "alarm"), ("4.99", "alarm"), ("5", "suspension_threshold")],
            "tracking": [("91", "ok"), ("90.99", "alarm"), ("90", "alarm"), ("89.99", "suspension_threshold")],
            "acceptance_hours": [("19.99", "ok"), ("20", "alarm"), ("23.99", "alarm"), ("24", "suspension_threshold")],
            "response_hours": [("19.99", "ok"), ("20", "alarm"), ("23.99", "alarm"), ("24", "suspension_threshold")],
        }
        for code, boundaries in cases.items():
            for value, expected in boundaries:
                with self.subTest(code=code, value=value):
                    self.assertEqual(classify(self.metric(code, value)), expected)

    def test_minimum_volume_0_29_30(self):
        for code, policy in self.policies.items():
            if not policy.is_mqc:
                continue
            breached_value = policy.suspension - Decimal("0.01") if policy.operator == "lt" else policy.suspension
            for orders in [0, 29]:
                with self.subTest(code=code, orders=orders):
                    self.assertEqual(classify(self.metric(code, str(breached_value), orders)), "insufficient_orders")
            self.assertEqual(classify(self.metric(code, str(breached_value), 30)), "suspension_threshold")

    def test_nps_and_delivery_are_independent_from_mqc(self):
        for code, reference in [("nps", 65), ("delivery", 90)]:
            self.assertEqual(classify(self.metric(code, str(reference), 0)), "ok")
            self.assertEqual(classify(self.metric(code, str(reference - 1), 0)), "below_reference")
        self.assertEqual(classify(self.metric("nps", "-100", 0)), "below_reference")

    def test_metric_validation(self):
        for code, value in [("acceptance", "100.01"), ("incidents", "-0.01"), ("nps", "-100.01"), ("response_hours", "-1")]:
            with self.subTest(code=code, value=value), self.assertRaises(ValidationError):
                self.metric(code, value).save()
        metric = self.metric("acceptance", "99")
        metric.period_end = date(2026, 8, 31)
        with self.assertRaises(ValidationError):
            metric.save()

    def test_nonmonthly_and_missing_measurements_are_not_evaluable(self):
        metric = self.metric("incidents", "6")
        metric.period_start = date(2026, 9, 24)
        self.assertEqual(classify(metric), "not_evaluable")
        metric.period_start = date(2026, 9, 1)
        metric.value = None
        self.assertEqual(classify(metric), "not_evaluable")
        metric.value = Decimal("6")
        metric.order_count = None
        self.assertEqual(classify(metric), "not_evaluable")

    def test_mqc_minimum_cannot_be_lowered_below_official_volume(self):
        metric = self.metric("incidents", "6", orders=29)
        metric.policy.minimum_orders = 0
        self.assertEqual(classify(metric), "insufficient_orders")
        with self.assertRaises(ValidationError):
            metric.policy.save()

    def test_monthly_calendar_and_rolling_windows(self):
        from quality.rules import is_monthly_period

        for start, end, expected in [
            (date(2026, 2, 1), date(2026, 2, 28), True),
            (date(2024, 2, 1), date(2024, 2, 29), True),
            (date(2026, 8, 15), date(2026, 9, 14), True),
            (date(2026, 8, 15), date(2026, 9, 15), False),
            (date(2026, 9, 1), date(2026, 10, 31), False),
            (date(2026, 12, 1), date(2026, 12, 31), True),
        ]:
            with self.subTest(start=start, end=end):
                self.assertEqual(is_monthly_period(start, end), expected)

    def test_persistence_uniqueness_and_policy_history(self):
        metric = self.metric("acceptance", "98.50")
        metric.save()
        metric.refresh_from_db()
        self.assertEqual(metric.value, Decimal("98.50"))
        self.assertEqual(classify(metric), "alarm")
        with self.assertRaises(ValidationError):
            self.metric("acceptance", "99").save()
        policy = metric.policy
        policy.alarm = Decimal("99.50")
        with self.assertRaises(ValidationError):
            policy.save()
        policy.pk = None
        policy.version = 2
        policy.save()
        metric.refresh_from_db()
        self.assertEqual(metric.policy.version, 1)

    def test_invalid_policy_configuration(self):
        policy = self.policies["nps"]
        policy.suspension = Decimal("60")
        with self.assertRaises(ValidationError):
            policy.save()
        policy = self.policies["incidents"]
        policy.suspension = Decimal("3")
        with self.assertRaises(ValidationError):
            policy.save()

    def test_database_rejects_invalid_period_even_without_model_save(self):
        metric = self.metric("acceptance", "99")
        metric.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            QualityMetric.objects.filter(pk=metric.pk).update(period_end=date(2026, 8, 1))

    @override_settings(DEBUG=True)
    def test_demo_is_idempotent_and_does_not_create_users(self):
        output = StringIO()
        call_command("seed_demo", owner="owner", stdout=output)
        call_command("seed_demo", owner="owner", stdout=output)
        self.assertEqual(QualityMetric.objects.count(), 14)
        self.assertEqual(get_user_model().objects.count(), 1)

    @override_settings(DEBUG=False)
    def test_demo_is_blocked_in_production(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", owner="owner")
