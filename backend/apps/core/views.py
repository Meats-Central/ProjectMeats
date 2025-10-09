from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ValidationError
import logging

logger = logging.getLogger(__name__)


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
            }
        )

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Signup endpoint to create new users.
    """
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("firstName", "")
    last_name = request.data.get("lastName", "")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)

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

    except Exception as e:
        return Response(
            {"error": f"Failed to create user: {str(e)}"},
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


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint that verifies database connectivity and system health.
    
    Returns:
        200: System is healthy with database connectivity
        503: System is unhealthy (database issues)
    """
    health_status = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "checks": {}
    }
    
    # Check database connectivity
    try:
        # Simple query to verify database is accessible
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Count users to verify we can query tables
        user_count = User.objects.count()
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "details": f"Connected, {user_count} users in database"
        }
        
    except Exception as e:
        logger.error(f"Health check database error: {str(e)}", exc_info=True)
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": "Database connection failed"
        }
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Check cache (optional)
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache_test = cache.get('health_check')
        health_status["checks"]["cache"] = {
            "status": "healthy" if cache_test == 'ok' else "degraded"
        }
    except Exception as e:
        logger.warning(f"Health check cache warning: {str(e)}")
        health_status["checks"]["cache"] = {
            "status": "degraded",
            "warning": "Cache not available"
        }
    
    return Response(health_status, status=status.HTTP_200_OK)

