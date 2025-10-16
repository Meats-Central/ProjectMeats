from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'preferences', views.UserPreferencesViewSet, basename='userpreferences')

urlpatterns = [
    path("auth/login/", views.login, name="login"),
    path("auth/guest-login/", views.guest_login, name="guest-login"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/logout/", views.logout, name="logout"),
    path("", include(router.urls)),
]
