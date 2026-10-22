from django.contrib import admin
from sellers.models import Seller


class SuperuserOnlyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission


@admin.register(Seller)
class SellerAdmin(SuperuserOnlyAdmin):
    list_display = ["name", "reference", "owner"]
    search_fields = ["name", "reference"]
