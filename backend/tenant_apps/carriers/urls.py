from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tenant_apps.carriers.views import CarrierViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"carriers", CarrierViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
