# Generated manually for adding tenant field to Supplier model

from django.db import migrations, models
import django.db.models.deletion


def set_default_tenant(apps, schema_editor):
    """Set all existing suppliers to the root tenant."""
    Supplier = apps.get_model('suppliers', 'Supplier')
    Tenant = apps.get_model('tenants', 'Tenant')
    
    try:
        root_tenant = Tenant.objects.get(slug='root')
        Supplier.objects.filter(tenant__isnull=True).update(tenant=root_tenant)
    except Tenant.DoesNotExist:
        pass  # No root tenant exists yet, skip


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        # Step 1: Add tenant field as nullable
        migrations.AddField(
            model_name='supplier',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suppliers',
                to='tenants.tenant',
                help_text='Tenant this supplier belongs to'
            ),
        ),
        # Step 2: Set existing records to root tenant
        migrations.RunPython(set_default_tenant, migrations.RunPython.noop),
        # Step 3: Make field required
        migrations.AlterField(
            model_name='supplier',
            name='tenant',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suppliers',
                to='tenants.tenant',
                help_text='Tenant this supplier belongs to'
            ),
        ),
        # Step 4: Add index for performance
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['tenant', 'name'], name='suppliers_s_tenant__idx'),
        ),
    ]
