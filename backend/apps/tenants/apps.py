from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenants"
    verbose_name = "Tenants"
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.tenants.signals  # noqa: F401
