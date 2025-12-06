# Generated migration to remove django-tenants schema-based models
# This migration removes the Client and Domain tables that were used for
# schema-based multi-tenancy. ProjectMeats now uses shared-schema approach.

from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration to remove schema-based multi-tenancy models.
    
    This migration:
    1. Drops the tenants_domain table (django-tenants Domain model)
    2. Drops the tenants_client table (django-tenants Client model)
    
    These tables are no longer needed as ProjectMeats uses shared-schema
    multi-tenancy with tenant_id foreign keys for data isolation.
    
    Note: RunSQL is used for better control over the DROP operation and
    to handle cases where tables may not exist (idempotent).
    """

    dependencies = [
        ("tenants", "0010_schema_based_client_domain"),
    ]

    operations = [
        # Drop the database tables using RunSQL for idempotent operation
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS tenants_domain CASCADE;",
                "DROP TABLE IF EXISTS tenants_client CASCADE;",
            ],
            reverse_sql=[
                # Reverse is a no-op - tables are not recreated
                # This is intentional as the models have been removed
                "SELECT 1;",
            ],
        ),
        # Remove model state from Django's migration tracking
        migrations.DeleteModel(name="Domain"),
        migrations.DeleteModel(name="Client"),
    ]
