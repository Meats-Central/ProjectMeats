"""
Core admin for ProjectMeats.

Admin interface for core models.
"""
from django.contrib import admin
from apps.core.models import Protein


@admin.register(Protein)
class ProteinAdmin(admin.ModelAdmin):
    """Admin interface for Protein model."""
    
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']