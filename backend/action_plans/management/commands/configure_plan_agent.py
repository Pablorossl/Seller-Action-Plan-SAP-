from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sellers.models import AGENT_GROUP


class Command(BaseCommand):
    help = "Habilita Admin de planes para un agente existente, con permisos explícitos y acceso a sus vendedores."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--interface-only", action="store_true", help="Concede permisos de React sin habilitar acceso a Admin.")

    @transaction.atomic
    def handle(self, *args, **options):
        user = get_user_model().objects.filter(username=options["username"], is_active=True).first()
        if user is None:
            raise CommandError("Crea primero un usuario activo; este comando no crea credenciales.")
        codenames = [f"{operation}_{model}" for model in ["improvementplan", "planmetric", "planaction"]
            for operation in ["add", "change", "view"]] + ["add_planreview", "view_planreview", "close_improvementplan"]
        permissions = Permission.objects.filter(content_type__app_label="action_plans", codename__in=codenames)
        if permissions.count() != len(codenames):
            raise CommandError("Ejecuta migrate antes de configurar permisos.")
        group, _ = Group.objects.get_or_create(name=AGENT_GROUP)
        user.groups.add(group)
        user.user_permissions.add(*permissions)
        if not options["interface_only"]:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        self.stdout.write(self.style.SUCCESS("Permisos de planes configurados; " + ("acceso Admin sin modificar." if options["interface_only"] else "Admin de planes propios habilitado.")))
