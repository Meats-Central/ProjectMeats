from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.plants.views import PlantViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'plants', PlantViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
