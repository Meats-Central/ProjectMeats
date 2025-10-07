"""
Health check views for ProjectMeats API.
Provides endpoints for monitoring application health and status.
"""

import psutil
import shutil
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status


@require_http_methods(["GET"])
@csrf_exempt
def health_check(request):
    """
    Basic health check endpoint.
    Returns application status and basic system info.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return JsonResponse(
        {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "database": db_status,
            "debug": settings.DEBUG,
        }
    )


@require_http_methods(["GET"])
@csrf_exempt
def health_detailed(request):
    """
    Detailed health check endpoint.
    Returns comprehensive system health information.
    """
    try:
        # Database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # System resource checks
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
        }

        # Disk usage
        disk = shutil.disk_usage("/")
        disk_usage = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100,
        }

        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)

        system_healthy = True
        system_issues = []

        # Check health thresholds
        if hasattr(settings, "HEALTH_CHECK"):
            if disk_usage["percent"] > settings.HEALTH_CHECK.get("DISK_USAGE_MAX", 90):
                system_healthy = False
                system_issues.append("disk_usage_high")

            if memory_usage["available"] / (1024 * 1024) < settings.HEALTH_CHECK.get(
                "MEMORY_MIN", 100
            ):
                system_healthy = False
                system_issues.append("memory_low")

    except Exception as e:
        memory_usage = disk_usage = cpu_usage = None
        system_healthy = False
        system_issues = [f"system_check_failed: {str(e)}"]

    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "unhealthy"
    elif not system_healthy:
        overall_status = "degraded"

    return JsonResponse(
        {
            "status": overall_status,
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "database": db_status,
                "system": "healthy" if system_healthy else "degraded",
            },
            "system": {
                "memory": memory_usage,
                "disk": disk_usage,
                "cpu": cpu_usage,
            },
            "issues": system_issues,
            "debug": settings.DEBUG,
        },
        status=status.HTTP_200_OK
        if overall_status == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@require_http_methods(["GET"])
@csrf_exempt
def ready_check(request):
    """
    Readiness check endpoint.
    Returns whether the application is ready to serve traffic.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {
                "status": "ready",
                "timestamp": timezone.now().isoformat(),
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "status": "not_ready",
                "timestamp": timezone.now().isoformat(),
                "error": str(e),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
