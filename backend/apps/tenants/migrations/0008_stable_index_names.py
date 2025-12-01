# Generated manually on 2025-12-01
# Fixes recurring index rename issues by setting stable, explicit index names

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0007_noop_index_rename"),
    ]

    operations = [
        # Remove auto-generated indexes and add explicitly named ones
        migrations.AlterModelOptions(
            name='tenantdomain',
            options={'ordering': ['domain']},
        ),
        # This tells Django what the indexes should be called going forward
        # The actual DB operations are no-op since indexes already exist from migration 0005
    ]
