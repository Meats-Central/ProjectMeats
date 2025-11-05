# Generated migration for extending Client model with business logic fields
# This adds ProjectMeats-specific fields to the Client model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_quotamodel'),
        ('tenants', '0005_client_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='meat_specialty',
            field=models.CharField(
                blank=True,
                choices=[('beef', 'Beef'), ('pork', 'Pork'), ('poultry', 'Poultry')],
                default='',
                help_text='Primary meat specialty for this client',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='client',
            name='logistics_integration_active',
            field=models.BooleanField(
                default=False,
                help_text='Activates custom logistics sync for this client'
            ),
        ),
        migrations.AddField(
            model_name='client',
            name='sales_quota_m2m',
            field=models.ManyToManyField(
                blank=True,
                help_text='Sales quotas associated with this client',
                related_name='clients',
                to='core.quotamodel'
            ),
        ),
    ]
