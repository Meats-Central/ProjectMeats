# Generated migration for reusable invitations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantinvitation',
            name='is_reusable',
            field=models.BooleanField(default=False, help_text='Allow multiple users to sign up with this token'),
        ),
        migrations.AddField(
            model_name='tenantinvitation',
            name='usage_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of times this invitation has been used'),
        ),
    ]
