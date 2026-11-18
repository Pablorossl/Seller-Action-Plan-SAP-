from django.contrib.auth.models import Group, Permission
from django.core.management.base import CommandError
from rest_framework.permissions import BasePermission
from sellers.models import AGENT_GROUP


class IsMarketplaceAgent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and (
            user.is_superuser or user.groups.filter(name=AGENT_GROUP).exists()
        ))


def grant_plan_permissions(user):
    codenames = [f"{operation}_{model}" for model in ["improvementplan", "planmetric", "planaction"]
        for operation in ["add", "change", "view"]] + ["add_planreview", "view_planreview", "close_improvementplan"]
    permissions = Permission.objects.filter(content_type__app_label="action_plans", codename__in=codenames)
    if permissions.count() != len(codenames):
        raise CommandError("Ejecuta migrate antes de configurar permisos.")
    group, _ = Group.objects.get_or_create(name=AGENT_GROUP)
    user.groups.add(group)
    user.user_permissions.add(*permissions)
