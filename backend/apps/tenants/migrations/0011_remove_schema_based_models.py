# Generated migration to remove django-tenants schema-based models
# This migration removes the Client and Domain tables that were used for
# schema-based multi-tenancy. ProjectMeats now uses shared-schema approach.

from django.db import migrations


class Migration(migrations.Migration):
    """
    Idempotent migration to remove schema-based multi-tenancy models.
    
    This migration:
    1. Drops the tenants_domain table (django-tenants Domain model) if it exists
    2. Drops the tenants_client table (django-tenants Client model) if it exists
    3. Removes model state from Django's migration tracking
    
    These tables are no longer needed as ProjectMeats uses shared-schema
    multi-tenancy with tenant_id foreign keys for data isolation.
    
    Note: Uses SeparateDatabaseAndState to handle both database operations
    and Django's internal model state tracking independently.
    """

    dependencies = [
        ("tenants", "0010_schema_based_client_domain"),
    ]

    operations = [
        # Separate database and state operations for proper handling
        migrations.SeparateDatabaseAndState(
            # Database operations: Drop tables if they exist (idempotent)
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "DROP TABLE IF EXISTS tenants_domain CASCADE;",
                        "DROP TABLE IF EXISTS tenants_client CASCADE;",
                    ],
                    reverse_sql=[
                        # Reverse is a no-op - tables are not recreated
                        "SELECT 1;",
                    ],
                ),
            ],
            # State operations: Remove models from Django's migration state
            # This only affects Django's internal tracking, not the database
            state_operations=[
                migrations.DeleteModel(name="Domain"),
                migrations.DeleteModel(name="Client"),
            ],
        ),
    ]
