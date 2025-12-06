# backend/apps/tenants/migrations/0013_tenant_schema_name.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0012_purge_legacy_architecture'),
    ]

    operations = [
        # OPERATIONS COMMENTED OUT TO PREVENT DUPLICATE COLUMN ERROR
        # migrations.AddField(
        #     model_name='tenant',
        #     name='schema_name',
        #     field=models.CharField(blank=True, db_index=True, help_text='Database schema name', max_length=63, null=True, unique=True),
        # ),
    ]
