from django.urls import path
from . import views

urlpatterns = [
    path("auth/login/", views.login, name="login"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/logout/", views.logout, name="logout"),
]
