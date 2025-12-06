# Generated migration for purging hybrid multi-tenancy debt
# Removes schema_name field and drops legacy django-tenants tables

from django.db import migrations, models, connection


def drop_legacy_tables(apps, schema_editor):
    """
    Drop legacy django-tenants tables (Client, Domain) if they exist.
    These were used in experimental schema-based multi-tenancy but are
    no longer needed in the shared-schema approach.
    """
    with connection.cursor() as cursor:
        # Drop tables in correct order (foreign key dependencies)
        cursor.execute("DROP TABLE IF EXISTS tenants_domain CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS tenants_client CASCADE;")


def reverse_drop_tables(apps, schema_editor):
    """Cannot recreate dropped tables - this migration is one-way."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0010_schema_based_client_domain'),
    ]

    operations = [
        # Step 1: Drop legacy django-tenants tables
        migrations.RunPython(
            code=drop_legacy_tables,
            reverse_code=reverse_drop_tables,
        ),
        
        # Step 2: Remove schema_name field from Tenant model
        migrations.RemoveField(
            model_name='tenant',
            name='schema_name',
        ),
    ]
