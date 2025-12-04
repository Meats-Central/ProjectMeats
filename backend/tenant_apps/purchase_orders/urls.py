from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tenant_apps.purchase_orders.views import PurchaseOrderViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"purchase-orders", PurchaseOrderViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
