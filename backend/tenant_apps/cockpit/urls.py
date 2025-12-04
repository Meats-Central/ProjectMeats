"""
URL routing for Cockpit app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CockpitSlotViewSet

router = DefaultRouter()
router.register(r'slots', CockpitSlotViewSet, basename='cockpit-slots')

urlpatterns = [
    path('', include(router.urls)),
]
