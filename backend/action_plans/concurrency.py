"""Conflictos recuperables y bloqueo común de las escrituras HTTP."""
import hashlib
import json

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import APIException

from action_plans.models import ImprovementPlan
from sellers.models import visible_sellers


class RevisionConflict(ValidationError):
    def __init__(self):
        super().__init__("El registro ha cambiado. Recarga sus datos y revisa tus cambios antes de guardarlos.")


def check_revision(instance, expected):
    if expected is not None and (type(expected) is not int or expected != instance.revision):
        raise RevisionConflict()


def lock_plan(user, pk):
    """Dentro de atomic(): asignación → plan. No bloquea otros vendedores."""
    seller_id = get_object_or_404(ImprovementPlan.objects.only("seller_id"), pk=pk).seller_id
    seller = get_object_or_404(visible_sellers(user).select_for_update(), pk=seller_id)
    return get_object_or_404(ImprovementPlan.objects.select_for_update(), pk=pk, seller=seller)


def request_identity(request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return {}
    key = serializers.UUIDField().run_validation(key)
    content = json.dumps([request.user.pk, request.path, request.data], sort_keys=True, separators=(",", ":"))
    return {"request_key": key, "request_hash": hashlib.sha256(content.encode()).hexdigest()}


def previous_request(model, identity):
    if not identity:
        return None
    previous = model.objects.filter(request_key=identity["request_key"]).first()
    if previous and previous.request_hash != identity["request_hash"]:
        error = APIException("Esta solicitud ya se utilizó con otros datos. Recarga antes de continuar.")
        error.status_code = 409
        raise error
    return previous
