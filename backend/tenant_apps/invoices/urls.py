"""URL configuration for invoices app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets when implemented
# router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = router.urls
