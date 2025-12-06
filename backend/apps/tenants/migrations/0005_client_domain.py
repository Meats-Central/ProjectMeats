# Migration for django-tenants integration
# Created to add Client and Domain models for schema-based multi-tenancy
# Based on django-tenants 3.5.0 TenantMixin and DomainMixin structure
# Made idempotent to handle cases where tables already exist
# NOTE: These models were later removed in migration 0011_remove_schema_based_models

from django.db import migrations, models, connection
import django.db.models.deletion
# django_tenants validator removed - these models are deprecated and removed in 0011


def create_tables_if_not_exist(apps, schema_editor):
    """Create tables only if they don't exist using raw SQL with IF NOT EXISTS"""
    with connection.cursor() as cursor:
        # Create tenants_client table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants_client (
                id BIGSERIAL PRIMARY KEY,
                schema_name VARCHAR(63) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create index on schema_name if it doesn't exist
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS tenants_client_schema_name_idx 
            ON tenants_client (schema_name);
        """)
        
        # Create tenants_domain table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants_domain (
                id BIGSERIAL PRIMARY KEY,
                domain VARCHAR(253) UNIQUE NOT NULL,
                is_primary BOOLEAN NOT NULL DEFAULT TRUE,
                tenant_id BIGINT NOT NULL
            );
        """)
        
        # Create indexes on tenants_domain if they don't exist
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS tenants_domain_domain_idx 
            ON tenants_domain (domain);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS tenants_domain_is_primary_idx 
            ON tenants_domain (is_primary);
        """)
        
        # Add foreign key constraint if it doesn't exist
        # First, check if both tables exist and clean up any orphaned records
        cursor.execute("""
            DO $$
            DECLARE
                tenant_id_type TEXT;
            BEGIN
                -- Check if both tables exist
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'tenants_client'
                ) AND EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'tenants_domain'
                ) THEN
                    -- Check the data type of tenant_id column
                    SELECT data_type INTO tenant_id_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public' 
                    AND table_name = 'tenants_domain' 
                    AND column_name = 'tenant_id';
                    
                    -- If tenant_id is UUID type (from old schema), drop and recreate column as BIGINT
                    IF tenant_id_type = 'uuid' THEN
                        -- Remove foreign key constraint if it exists
                        IF EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'tenants_domain_tenant_id_fk'
                        ) THEN
                            ALTER TABLE tenants_domain DROP CONSTRAINT tenants_domain_tenant_id_fk;
                        END IF;
                        
                        -- Drop the UUID column and recreate as BIGINT
                        ALTER TABLE tenants_domain DROP COLUMN tenant_id;
                        ALTER TABLE tenants_domain ADD COLUMN tenant_id BIGINT NOT NULL DEFAULT 0;
                        
                        -- Clean up the default value (it was just for adding the column)
                        ALTER TABLE tenants_domain ALTER COLUMN tenant_id DROP DEFAULT;
                    END IF;
                    
                    -- Clean up any orphaned records in tenants_domain (now that types match)
                    DELETE FROM tenants_domain 
                    WHERE tenant_id NOT IN (SELECT id FROM tenants_client);
                    
                    -- Add constraint if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'tenants_domain_tenant_id_fk'
                    ) THEN
                        ALTER TABLE tenants_domain 
                        ADD CONSTRAINT tenants_domain_tenant_id_fk 
                        FOREIGN KEY (tenant_id) 
                        REFERENCES tenants_client(id) 
                        ON DELETE CASCADE;
                    END IF;
                END IF;
            END $$;
        """)


def reverse_tables(apps, schema_editor):
    """Drop tables if they exist"""
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS tenants_domain CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS tenants_client CASCADE;")


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0004_add_schema_name_and_domain_model'),
    ]

    operations = [
        # Use RunPython with raw SQL to create tables idempotently
        migrations.RunPython(
            code=create_tables_if_not_exist,
            reverse_code=reverse_tables,
        ),
        # Add model state without database operations
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Client',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('schema_name', models.CharField(db_index=True, max_length=63, unique=True)),
                        ('name', models.CharField(help_text='Client organization name', max_length=255)),
                        ('description', models.TextField(blank=True, help_text='Optional description of the client')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'db_table': 'tenants_client',
                        'abstract': False,
                    },
                ),
                migrations.CreateModel(
                    name='Domain',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('domain', models.CharField(db_index=True, max_length=253, unique=True)),
                        ('is_primary', models.BooleanField(db_index=True, default=True)),
                        ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='tenants.client')),
                    ],
                    options={
                        'db_table': 'tenants_domain',
                        'abstract': False,
                    },
                ),
            ],
            # No database operations - already handled by RunPython above
            database_operations=[],
        ),
    ]
