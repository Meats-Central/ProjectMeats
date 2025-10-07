"""
Bug Reports app configuration.
"""
from django.apps import AppConfig


class BugReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.bug_reports"
    verbose_name = "Bug Reports"
