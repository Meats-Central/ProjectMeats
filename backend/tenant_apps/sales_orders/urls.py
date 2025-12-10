"""URL configuration for sales_orders app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets when implemented
# router.register(r'sales-orders', SalesOrderViewSet, basename='sales-order')

urlpatterns = router.urls
