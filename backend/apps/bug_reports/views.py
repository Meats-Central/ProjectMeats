"""
Bug Reports views for ProjectMeats.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import BugReport
from .serializers import BugReportSerializer


class BugReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bug reports.

    Provides CRUD operations for bug reports with filtering and search.
    """

    queryset = BugReport.objects.all()
    serializer_class = BugReportSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "severity", "category", "reporter"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "severity"]
    ordering = ["-created_at"]
