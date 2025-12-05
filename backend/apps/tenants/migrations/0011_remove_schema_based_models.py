# Generated migration to remove django-tenants schema-based models
# This migration removes the Client and Domain tables that were used for
# schema-based multi-tenancy. ProjectMeats now uses shared-schema approach.

from django.db import migrations, connection


def drop_tables_if_exist(apps, schema_editor):
    """Drop Client and Domain tables if they exist."""
    with connection.cursor() as cursor:
        # Drop tenants_domain first (has FK to tenants_client)
        cursor.execute("DROP TABLE IF EXISTS tenants_domain CASCADE;")
        # Drop tenants_client
        cursor.execute("DROP TABLE IF EXISTS tenants_client CASCADE;")


def reverse_noop(apps, schema_editor):
    """No-op reverse operation - tables are not recreated."""
    pass


class Migration(migrations.Migration):
    """
    Migration to remove schema-based multi-tenancy models.
    
    This migration:
    1. Drops the tenants_client table (django-tenants Client model)
    2. Drops the tenants_domain table (django-tenants Domain model)
    
    These tables are no longer needed as ProjectMeats uses shared-schema
    multi-tenancy with tenant_id foreign keys for data isolation.
    """

    dependencies = [
        ("tenants", "0010_schema_based_client_domain"),
    ]

    operations = [
        # Drop the database tables
        migrations.RunPython(
            code=drop_tables_if_exist,
            reverse_code=reverse_noop,
        ),
        # Remove model state
        migrations.DeleteModel(name="Domain"),
        migrations.DeleteModel(name="Client"),
    ]
