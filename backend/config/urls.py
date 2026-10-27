from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from config.views import dashboard, home
from quality.views import QualityMetricViewSet
from sellers.views import SellerViewSet
from action_plans.views import PlanViewSet, overview, responsibles, workspace

router = DefaultRouter()
router.register("sellers", SellerViewSet, basename="seller")
router.register("metrics", QualityMetricViewSet, basename="metric")
router.register("plans", PlanViewSet, basename="plan")
urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("api/workspace/", workspace, name="workspace"),
    path("api/overview/", overview, name="overview"),
    path("api/responsibles/", responsibles, name="responsibles"),
    path("api/", include(router.urls)),
]
