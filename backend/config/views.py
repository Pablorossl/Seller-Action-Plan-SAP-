from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from sellers.models import visible_sellers


@never_cache
@login_required
def home(request):
    return render(request, "home.html", {"sellers": visible_sellers(request.user)})


@never_cache
@login_required
def dashboard(request):
    return render(request, "index.html")
