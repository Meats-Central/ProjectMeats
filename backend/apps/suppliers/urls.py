from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.suppliers.views import SupplierViewSet

app_name = "suppliers"

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
