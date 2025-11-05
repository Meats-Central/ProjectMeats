# Generated migration for QuotaModel
# This adds a QuotaModel to support sales quota management

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_userpreferences'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name of the quota (e.g., 'Q4 2024 Sales Target')", max_length=255)),
                ('target_amount', models.IntegerField(default=0, help_text='Target amount for this quota (in applicable units)')),
                ('description', models.TextField(blank=True, default='', help_text='Optional description of the quota')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Quota',
                'verbose_name_plural': 'Quotas',
                'ordering': ['-created_at'],
            },
        ),
    ]
