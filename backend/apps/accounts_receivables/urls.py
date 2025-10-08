from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts_receivables.views import AccountsReceivableViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"accounts-receivables", AccountsReceivableViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
