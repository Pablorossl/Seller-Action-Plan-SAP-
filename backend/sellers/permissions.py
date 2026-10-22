from rest_framework.permissions import BasePermission
from sellers.models import AGENT_GROUP


class IsMarketplaceAgent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and (
            user.is_superuser or user.groups.filter(name=AGENT_GROUP).exists()
        ))
