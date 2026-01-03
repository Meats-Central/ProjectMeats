from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenants"

    def ready(self):
        """Import signals when app is ready."""
        import apps.tenants.signals  # noqa: F401
    verbose_name = "Tenants"
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.tenants.signals  # noqa: F401
