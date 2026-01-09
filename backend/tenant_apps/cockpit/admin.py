"""
Admin configuration for Cockpit app.
"""
from django.contrib import admin
from .models import ActivityLog, ScheduledCall


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_id', 'title', 'created_by', 'created_on', 'is_pinned')
    list_filter = ('entity_type', 'is_pinned', 'created_on')
    search_fields = ('title', 'content', 'tags')
    readonly_fields = ('created_on', 'modified_on')


@admin.register(ScheduledCall)
class ScheduledCallAdmin(admin.ModelAdmin):
    list_display = ('title', 'entity_type', 'entity_id', 'scheduled_for', 'is_completed', 'assigned_to')
    list_filter = ('entity_type', 'is_completed', 'scheduled_for')
    search_fields = ('title', 'description')
    readonly_fields = ('created_on', 'modified_on', 'completed_at')

