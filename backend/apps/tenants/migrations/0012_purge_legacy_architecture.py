# Generated migration to purge django-tenants legacy architecture
# This migration removes database tables from the old schema-based approach.
# ProjectMeats now uses a strict shared-schema multi-tenancy approach.

from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration to purge django-tenants legacy architecture.
    
    This migration:
    1. Drops the tenants_client table (django-tenants Client model)
    2. Drops the tenants_domain table (django-tenants Domain model)
    
    These tables are artifacts from a previous django-tenants implementation
    that used schema-based multi-tenancy. ProjectMeats now strictly uses
    shared-schema multi-tenancy with tenant_id foreign keys for data isolation.
    
    Note: This migration is idempotent using DROP TABLE IF EXISTS.
    """

    dependencies = [
        ("tenants", "0011_remove_schema_based_models"),
    ]

    operations = [
        # Drop the legacy django-tenants tables using RunSQL for idempotent operation
        migrations.RunSQL(
            sql=[
                # Drop tables in correct order (domain references client)
                "DROP TABLE IF EXISTS tenants_domain CASCADE;",
                "DROP TABLE IF EXISTS tenants_client CASCADE;",
            ],
            reverse_sql=[
                # Reverse is a no-op - tables are not recreated
                # This is intentional as the models have been removed
                # and we are moving to strict shared-schema architecture
                "SELECT 1;",
            ],
        ),
    ]
