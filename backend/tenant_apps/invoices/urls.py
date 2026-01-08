"""URL configuration for invoices app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, ClaimViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'claims', ClaimViewSet, basename='claim')

urlpatterns = [
    path('', include(router.urls)),
]

