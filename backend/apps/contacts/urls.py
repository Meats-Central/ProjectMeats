from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.contacts.views import ContactViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'contacts', ContactViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
