from apps.tenants.models import Tenant, TenantUser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils.text import slugify
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


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
        user_tenants = (
            TenantUser.objects.filter(user=user, is_active=True)
            .select_related("tenant")
            .values("tenant__id", "tenant__name", "tenant__slug", "role")
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
        guest_username = "guest"
        guest_user = User.objects.get(username=guest_username)

        if not guest_user.is_active:
            return Response(
                {"error": "Guest account is currently disabled"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Get or create token for guest user
        token, created = Token.objects.get_or_create(user=guest_user)

        # Get guest tenant info
        guest_tenant_user = (
            TenantUser.objects.filter(user=guest_user, is_active=True)
            .select_related("tenant")
            .first()
        )

        if not guest_tenant_user:
            return Response(
                {
                    "error": (
                        "Guest tenant not configured. "
                        "Please run: python manage.py create_guest_tenant"
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                "message": "Welcome to ProjectMeats! You are logged in as a guest user.",
            }
        )

    except User.DoesNotExist:
        return Response(
            {
                "error": (
                    "Guest account not found. "
                    "Please run: python manage.py create_guest_tenant"
                ),
                "setup_command": "python manage.py create_guest_tenant",
            },
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Open signup endpoint - creates a new user account with their own tenant.

    Each user who signs up gets their own tenant where they are the owner.
    This allows immediate access to the system for testing and evaluation.
    """
    # Extract and validate required fields
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("firstName", "")
    last_name = request.data.get("lastName", "")

    # Validation
    if not username:
        return Response(
            {"error": "Username is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not password:
        return Response(
            {"error": "Password is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Use atomic transaction to ensure all-or-nothing creation
        with transaction.atomic():
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            # Create a personal tenant for the user
            tenant_slug = slugify(f"{username}-{user.id}")
            tenant = Tenant.objects.create(
                name=f"{first_name or username}'s Workspace",
                slug=tenant_slug,
                contact_email=email,
                created_by=user,
                is_active=True,
                is_trial=True,
            )

            # Associate user with tenant as owner
            TenantUser.objects.create(
                tenant=tenant,
                user=user,
                role="owner",
                is_active=True,
            )

            # Create auth token
            token, _ = Token.objects.get_or_create(user=user)

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
            },
            status=status.HTTP_201_CREATED,
        )

    except IntegrityError as e:
        # Database constraint violation (e.g., duplicate slug)
        return Response(
            {"error": f"Failed to create account: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        # Unexpected errors
        return Response(
            {"error": f"Failed to create account: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
