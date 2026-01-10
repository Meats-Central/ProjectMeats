"""
URL configuration for products app.

Registers ProductViewSet for /api/v1/products/ endpoint.
Uses shared-schema multi-tenancy with tenant filtering in viewset.
"""
import logging
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

logger = logging.getLogger(__name__)

router = DefaultRouter()

# Register ProductViewSet
try:
    router.register(r'products', ProductViewSet, basename='product')
    logger.info("✅ ProductViewSet registered at /api/v1/products/")
except Exception as e:
    logger.error(f"❌ Failed to register ProductViewSet: {e}")

urlpatterns = router.urls
