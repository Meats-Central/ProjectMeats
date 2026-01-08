"""URL configuration for invoices app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, ClaimViewSet, PaymentTransactionViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'payments', PaymentTransactionViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]

