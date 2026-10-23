"""Reglas compartidas; umbrales de referencia consultados el 23/10/2026."""
from calendar import monthrange
from datetime import date, timedelta

from django.core.exceptions import ValidationError


MQC_MINIMUM_ORDERS = 30


DEFAULT_POLICIES = [
    ("acceptance", "percent", "lt", "99", "98", True),
    ("incidents", "percent", "gte", "4", "5", True),
    ("tracking", "percent", "lt", "91", "90", True),
    ("acceptance_hours", "hours", "gte", "20", "24", True),
    ("response_hours", "hours", "gte", "20", "24", True),
    ("nps", "percent", "lt", "65", None, False),
    ("delivery", "percent", "lt", "90", None, False),
]


def validate_value(policy, value):
    if value is None:
        return
    lower = -100 if policy.code == "nps" else 0
    if not value.is_finite() or value < lower or (policy.unit == "percent" and value > 100):
        raise ValidationError("Valor fuera del rango del indicador.")


def is_monthly_period(start: date | None, end: date | None) -> bool:
    """Mes natural o ventana móvil de un mes, con ambos extremos incluidos."""
    if start is None or end is None:
        return False
    year, month = (start.year + 1, 1) if start.month == 12 else (start.year, start.month + 1)
    if year > 9999:
        return False
    next_month = date(year, month, min(start.day, monthrange(year, month)[1]))
    return end == next_month - timedelta(days=1)
