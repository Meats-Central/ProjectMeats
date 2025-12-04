from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tenant_apps.customers.views import CustomerViewSet

app_name = "customers"

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"customers", CustomerViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
