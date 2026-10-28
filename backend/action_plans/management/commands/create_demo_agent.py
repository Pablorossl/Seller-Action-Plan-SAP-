"""Alta interactiva, sin contraseña en argv, logs ni variables de build."""
from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction


class Command(BaseCommand):
    help = "Crea una cuenta de evaluación sin privilegios administrativos. Solicita contraseña por terminal."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username=options["username"]).exists():
            raise CommandError("El usuario ya existe; no se modifican cuentas ni contraseñas.")
        user = User(username=options["username"], is_staff=False, is_superuser=False)
        password = getpass("Contraseña de evaluación: ")
        if password != getpass("Repite la contraseña: "):
            raise CommandError("Las contraseñas no coinciden.")
        try:
            validate_password(password, user)
            user.full_clean(exclude=["password"])
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc
        user.set_password(password)
        user.save()
        call_command("configure_plan_agent", username=user.username, interface_only=True, stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS("Cuenta creada. Comparte el acceso con el tribunal mediante un canal privado."))
