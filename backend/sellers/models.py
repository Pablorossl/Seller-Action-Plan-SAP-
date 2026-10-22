from django.conf import settings
from django.db import models

AGENT_GROUP = "Marketplace Agent"


class Seller(models.Model):
    name = models.CharField("nombre", max_length=160)
    reference = models.CharField("referencia ficticia", max_length=40, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sellers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


def visible_sellers(user):
    if not user.is_authenticated:
        return Seller.objects.none()
    if user.is_superuser:
        return Seller.objects.all()
    if user.groups.filter(name=AGENT_GROUP).exists():
        return Seller.objects.filter(owner=user)
    return Seller.objects.none()
