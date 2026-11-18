from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from sellers.permissions import grant_plan_permissions
from sellers.models import AGENT_GROUP, Seller, WorkspaceProfile, is_workspace_admin


User = get_user_model()


class WorkspaceAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_workspace_admin(request.user)


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "role", "password"]

    def get_role(self, user):
        return "ADMIN" if is_workspace_admin(user) else "AGENT"

    def validate(self, attrs):
        writable = {"username", "first_name", "last_name", "email", "is_active"}
        if not self.instance:
            writable.add("password")
        if set(self.initial_data) - writable:
            raise serializers.ValidationError("La petición contiene campos que no se pueden modificar.")
        if not self.instance:
            candidate = User(**{key: value for key, value in attrs.items() if key != "password"})
            try:
                validate_password(attrs["password"], candidate)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Configure the established action-plan permissions even for initially inactive accounts.
        grant_plan_permissions(user)
        WorkspaceProfile.objects.create(user=user)
        return user


def workspace_users():
    return User.objects.filter(Q(groups__name=AGENT_GROUP) | Q(workspace_profile__is_admin=True)
                               | Q(is_superuser=True)).distinct().select_related("workspace_profile").order_by("username")


@never_cache
@api_view(["GET", "POST"])
@permission_classes([WorkspaceAdmin])
def accounts(request):
    if request.method == "GET":
        return Response({"users": AccountSerializer(workspace_users(), many=True).data,
                         "sellers": list(Seller.objects.values("id", "name", "reference", "owner_id"))})
    return save_account(request)


def save_account(request, instance=None):
    serializer = AccountSerializer(instance, data=request.data, partial=instance is not None)
    serializer.is_valid(raise_exception=True)
    try:
        with transaction.atomic():
            serializer.save()
    except IntegrityError:
        if not User.objects.filter(username=User.normalize_username(request.data.get("username", ""))).exists():
            raise
        raise serializers.ValidationError({"username": "El nombre de usuario ya está ocupado."})
    return Response(serializer.data, status=200 if instance else 201)


@never_cache
@api_view(["PATCH"])
@permission_classes([WorkspaceAdmin])
@transaction.atomic
def account(request, pk):
    user = get_object_or_404(User.objects.select_for_update(), pk=pk, pk__in=workspace_users().values("pk"))
    if is_workspace_admin(user):
        raise PermissionDenied("La gestión de cuentas permite editar agentes.")
    return save_account(request, user)


class AssignmentSerializer(serializers.Serializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.none(), allow_null=True)
    previous_owner = serializers.IntegerField(allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = workspace_users().filter(is_active=True)


@never_cache
@api_view(["PATCH"])
@permission_classes([WorkspaceAdmin])
@transaction.atomic
def assignment(request, pk):
    seller = get_object_or_404(Seller.objects.select_for_update(), pk=pk)
    form = AssignmentSerializer(data=request.data)
    form.is_valid(raise_exception=True)
    if seller.owner_id != form.validated_data["previous_owner"]:
        return Response({"detail": "La asignación ha cambiado. Recarga los datos."}, status=409)
    seller.owner = form.validated_data["owner"]
    seller.save(update_fields=["owner"])
    return Response({"owner_id": seller.owner_id})


@never_cache
@api_view(["POST"])
def finish_onboarding(request):
    WorkspaceProfile.objects.filter(user=request.user).update(onboarding_pending=False)
    return Response(status=204)
