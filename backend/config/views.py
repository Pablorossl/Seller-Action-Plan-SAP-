from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe
from django.db import connection, DatabaseError
from django.http import JsonResponse

from sellers.models import visible_sellers


@never_cache
@login_required
def home(request):
    return render(request, "home.html", {"sellers": visible_sellers(request.user)})


@never_cache
@login_required
def dashboard(request):
    return render(request, "index.html")


@never_cache
@require_safe
def health(request):
    """Readiness: confirma SQL y esquema, sin exponer configuración ni registros."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sellers_seller LIMIT 1")
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
