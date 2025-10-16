from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ValidationError
from apps.tenants.models import Tenant, TenantUser
from .models import UserPreferences
from .serializers import UserPreferencesSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint for token-based authentication.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user's tenants
        user_tenants = TenantUser.objects.filter(
            user=user,
            is_active=True
        ).select_related('tenant').values(
            'tenant__id',
            'tenant__name',
            'tenant__slug',
            'role'
        )
        
        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                },
                "tenants": list(user_tenants),
            }
        )

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def guest_login(request):
    """
    Guest login endpoint - automatically logs in as the guest user.
    
    This allows users to try ProjectMeats without creating an account.
    The guest user has admin-level permissions within the guest tenant,
    but is NOT a superuser.
    """
    try:
        # Get guest user (default username: 'guest')
        guest_username = 'guest'
        guest_user = User.objects.get(username=guest_username)
        
        if not guest_user.is_active:
            return Response(
                {"error": "Guest account is currently disabled"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Get or create token for guest user
        token, created = Token.objects.get_or_create(user=guest_user)
        
        # Get guest tenant info
        guest_tenant_user = TenantUser.objects.filter(
            user=guest_user,
            is_active=True
        ).select_related('tenant').first()
        
        if not guest_tenant_user:
            return Response(
                {"error": "Guest tenant not configured. Please run: python manage.py create_guest_tenant"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {
                "token": token.key,
                "user": {
                    "id": guest_user.id,
                    "username": guest_user.username,
                    "email": guest_user.email,
                    "first_name": guest_user.first_name,
                    "last_name": guest_user.last_name,
                    "is_staff": guest_user.is_staff,
                    "is_superuser": guest_user.is_superuser,
                    "is_active": guest_user.is_active,
                },
                "tenant": {
                    "id": str(guest_tenant_user.tenant.id),
                    "name": guest_tenant_user.tenant.name,
                    "slug": guest_tenant_user.tenant.slug,
                    "role": guest_tenant_user.role,
                    "is_guest": True,
                },
                "message": "Welcome to ProjectMeats! You are logged in as a guest user."
            }
        )
        
    except User.DoesNotExist:
        return Response(
            {
                "error": "Guest account not found. Please run: python manage.py create_guest_tenant",
                "setup_command": "python manage.py create_guest_tenant"
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    DEPRECATED: Open signup is disabled. Use invitation-based signup.
    
    Registration is now invite-only to ensure all users are properly associated
    with a tenant. Users must sign up using an invitation link.
    """
    return Response(
        {
            "error": "Open registration is disabled.",
            "message": "Registration is invite-only. Please contact your tenant administrator for an invitation link.",
            "endpoint": "Use /api/tenants/api/auth/signup-with-invitation/ instead"
        },
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(["POST"])
def logout(request):
    """
    Logout endpoint that deletes the user's token.
    """
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message": "Successfully logged out"})
    except Token.DoesNotExist:
        return Response({"message": "Already logged out"})


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user preferences.
    
    Provides endpoints for getting and updating user preferences including
    theme, sidebar state, and dashboard layout.
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter to current user's preferences only."""
        return UserPreferences.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create preferences for the current user."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's preferences."""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_theme(self, request):
        """Update only the theme preference."""
        preferences = self.get_object()
        theme = request.data.get('theme')
        if theme not in ['light', 'dark']:
            return Response(
                {'error': 'Invalid theme. Must be "light" or "dark"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        preferences.theme = theme
        preferences.save()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_sidebar(self, request):
        """Update only the sidebar state."""
        preferences = self.get_object()
        sidebar_open = request.data.get('sidebar_open')
        if not isinstance(sidebar_open, bool):
            return Response(
                {'error': 'sidebar_open must be a boolean'},
                status=status.HTTP_400_BAD_REQUEST
            )
        preferences.sidebar_open = sidebar_open
        preferences.save()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_dashboard_layout(self, request):
        """Update dashboard layout configuration."""
        preferences = self.get_object()
        dashboard_layout = request.data.get('dashboard_layout')
        if not isinstance(dashboard_layout, dict):
            return Response(
                {'error': 'dashboard_layout must be a JSON object'},
                status=status.HTTP_400_BAD_REQUEST
            )
        preferences.dashboard_layout = dashboard_layout
        preferences.save()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

