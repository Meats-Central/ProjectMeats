# Generated manually for Golden Ticket reusable invitations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_merge_20260102_0100'),
    ]

    operations = [
        # Add max_uses field
        migrations.AddField(
            model_name='tenantinvitation',
            name='max_uses',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Maximum number of times this token can be used'
            ),
        ),
        
        # Make email optional (nullable)
        migrations.AlterField(
            model_name='tenantinvitation',
            name='email',
            field=models.EmailField(
                blank=True,
                null=True,
                help_text='Email address (optional for reusable links)'
            ),
        ),
        
        # Remove old constraint
        migrations.RemoveConstraint(
            model_name='tenantinvitation',
            name='unique_pending_invitation_per_tenant_email',
        ),
        
        # Add new constraint (only for non-null emails)
        migrations.AddConstraint(
            model_name='tenantinvitation',
            constraint=models.UniqueConstraint(
                fields=['tenant', 'email'],
                condition=models.Q(status='pending', email__isnull=False),
                name='unique_pending_invitation_per_tenant_email'
            ),
        ),
    ]
