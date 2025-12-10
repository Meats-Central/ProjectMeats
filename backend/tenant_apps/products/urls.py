"""URL configuration for products app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets when implemented
# router.register(r'products', ProductViewSet, basename='product')

urlpatterns = router.urls
