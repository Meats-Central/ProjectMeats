# Generated migration - schema-based compatibility
# Modified to remove django_tenants dependency

from django.db import migrations, models
import django.db.models.deletion


def _check_schema_name(value):
    """Dummy validator for schema_name - no longer used."""
    return value


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0009_fix_index_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="schema_name",
            field=models.CharField(
                db_index=True,
                max_length=63,
                unique=True,
                validators=[_check_schema_name],
            ),
        ),
        migrations.AlterField(
            model_name="domain",
            name="domain",
            field=models.CharField(db_index=True, max_length=253, unique=True),
        ),
        migrations.AlterField(
            model_name="domain",
            name="is_primary",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name="domain",
            name="tenant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="domains",
                to="tenants.client",
            ),
        ),
    ]
