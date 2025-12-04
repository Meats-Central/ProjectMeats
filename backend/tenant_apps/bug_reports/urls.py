from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BugReportViewSet

router = DefaultRouter()
router.register(r"", BugReportViewSet, basename="bugreport")

urlpatterns = [
    path("", include(router.urls)),
]
