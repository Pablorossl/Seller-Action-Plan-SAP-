from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from config.views import dashboard, home, health, portal, WorkspaceLogin
from quality.views import QualityMetricViewSet
from sellers.accounts import accounts, account, assignment, finish_onboarding
from sellers.views import SellerViewSet
from action_plans.views import PlanViewSet, overview, responsibles, workspace

router = DefaultRouter()
router.register("sellers", SellerViewSet, basename="seller")
router.register("metrics", QualityMetricViewSet, basename="metric")
router.register("plans", PlanViewSet, basename="plan")
urlpatterns = [
    path("healthz/", health, name="health"),
    path("", home, name="home"),
    path("portal/", portal, name="portal"),
    path("dashboard/", dashboard, name="dashboard"),
    path("accounts/login/", WorkspaceLogin.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/login/", WorkspaceLogin.as_view()),
    path("admin/", admin.site.urls),
    path("api/workspace/", workspace, name="workspace"),
    path("api/users/", accounts),
    path("api/users/<int:pk>/", account),
    path("api/assignments/<int:pk>/", assignment),
    path("api/onboarding/complete/", finish_onboarding),
    path("api/overview/", overview, name="overview"),
    path("api/responsibles/", responsibles, name="responsibles"),
    path("api/", include(router.urls)),
]
