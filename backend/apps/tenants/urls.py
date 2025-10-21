from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, TenantUserViewSet
from .invitation_views import (
    TenantInvitationViewSet,
    signup_with_invitation,
    validate_invitation
)

router = DefaultRouter()
router.register(r"tenants", TenantViewSet)
router.register(r"tenant-users", TenantUserViewSet)
router.register(r"invitations", TenantInvitationViewSet, basename='tenant-invitation')

app_name = "tenants"

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/invitations/validate/", validate_invitation, name='validate-invitation'),
    path("api/auth/signup-with-invitation/", signup_with_invitation, name='signup-with-invitation'),
]
