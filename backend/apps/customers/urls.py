from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.customers.views import CustomerViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
