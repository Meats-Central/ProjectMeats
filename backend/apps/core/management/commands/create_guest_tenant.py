"""
Management command to create a default guest tenant and guest user.
This allows users to try the system without signing up.

The guest user has staff permissions for testing/demo purposes
(can access Django admin) but is NOT a superuser (no system-wide access).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.tenants.models import Tenant, TenantUser

User = get_user_model()


class Command(BaseCommand):
    help = "Create default guest tenant and guest user for demo/trial purposes"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='guest',
            help='Username for the guest user (default: guest)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='guest123',
            help='Password for the guest user (default: guest123)'
        )
        parser.add_argument(
            '--tenant-name',
            type=str,
            default='Guest Demo Organization',
            help='Name for the guest tenant (default: Guest Demo Organization)'
        )
        parser.add_argument(
            '--tenant-slug',
            type=str,
            default='guest-demo',
            help='Slug for the guest tenant (default: guest-demo)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        tenant_name = options['tenant_name']
        tenant_slug = options['tenant_slug']

        try:
            with transaction.atomic():
                # 1. Create or get guest user
                guest_user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@guest.projectmeats.local',
                        'first_name': 'Guest',
                        'last_name': 'User',
                        'is_staff': True,  # Staff (can access Django admin for testing)
                        'is_superuser': False,  # NOT superuser (no system-wide access)
                        'is_active': True,
                    }
                )

                if user_created:
                    guest_user.set_password(password)
                    guest_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created guest user: {username} (staff=True, superuser=False)'
                        )
                    )
                else:
                    # Update existing guest user to be staff
                    if not guest_user.is_staff:
                        guest_user.is_staff = True
                        guest_user.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Updated guest user to staff: {username}'
                            )
                        )
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Guest user already exists: {username} (staff={guest_user.is_staff}, superuser={guest_user.is_superuser})'
                        )
                    )

                # 2. Create or get guest tenant
                guest_tenant, tenant_created = Tenant.objects.get_or_create(
                    slug=tenant_slug,
                    defaults={
                        'name': tenant_name,
                        'contact_email': f'admin@{tenant_slug}.projectmeats.local',
                        'contact_phone': '+1-555-GUEST-00',
                        'is_active': True,
                        'is_trial': True,  # Mark as trial
                        'created_by': guest_user,
                        'settings': {
                            'is_guest_tenant': True,  # Mark as guest tenant
                            'allow_data_reset': True,  # Allow periodic data cleanup
                            'max_records': 100,  # Limit record creation
                            'description': 'Demo organization for guest users to explore ProjectMeats features'
                        }
                    }
                )

                if tenant_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created guest tenant: {tenant_name} ({tenant_slug})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Guest tenant already exists: {tenant_name}'
                        )
                    )

                # 3. Associate guest user with guest tenant as admin
                tenant_user, tu_created = TenantUser.objects.get_or_create(
                    tenant=guest_tenant,
                    user=guest_user,
                    defaults={
                        'role': 'admin',  # Admin role (NOT owner, to prevent tenant deletion)
                        'is_active': True,
                    }
                )

                if tu_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Associated {username} with {tenant_name} (role: admin)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Guest user already associated with tenant (role: {tenant_user.role})'
                        )
                    )

                # 4. Grant Django admin permissions for tenant-scoped models
                self._grant_permissions(guest_user)

                # 5. Summary
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('=' * 60))
                self.stdout.write(self.style.SUCCESS('GUEST MODE SETUP COMPLETE'))
                self.stdout.write(self.style.SUCCESS('=' * 60))
                self.stdout.write('')
                self.stdout.write(f'Guest Username: {username}')
                self.stdout.write(f'Guest Password: {password}')
                self.stdout.write(f'Tenant Name: {tenant_name}')
                self.stdout.write(f'Tenant Slug: {tenant_slug}')
                self.stdout.write(f'Role: admin (tenant-level)')
                self.stdout.write(f'Staff: Yes (can access Django admin for testing)')
                self.stdout.write(f'Superuser: No (no system-wide access)')
                self.stdout.write('')
                self.stdout.write('Guest user can:')
                self.stdout.write('  ✓ Access Django admin at /admin/ (for testing)')
                self.stdout.write('  ✓ View tenant-scoped data in admin')
                self.stdout.write('  ✓ Full CRUD within guest tenant via API/frontend')
                self.stdout.write('')
                self.stdout.write('Guest user CANNOT:')
                self.stdout.write('  ✗ Manage users/permissions (not superuser)')
                self.stdout.write('  ✗ Access system-wide settings')
                self.stdout.write('  ✗ View/modify other tenants\' data')
                self.stdout.write('')
                self.stdout.write('Users can now log in with these credentials to try ProjectMeats!')
                self.stdout.write('')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating guest setup: {str(e)}')
            )
            raise

    def _grant_permissions(self, user):
        """
        Grant Django admin permissions for tenant-scoped models.
        
        Grants view, add, change, delete permissions for:
        - Customers
        - Suppliers
        - Contacts
        - Products
        - Purchase Orders
        - Sales Orders
        - Invoices
        - Accounts Receivables
        - Carriers
        - Plants
        
        Does NOT grant permissions for:
        - User management (auth.User, auth.Group)
        - Tenant management (tenants.Tenant, tenants.TenantUser)
        - System settings
        """
        from tenant_apps.customers.models import Customer
        from tenant_apps.suppliers.models import Supplier
        from tenant_apps.contacts.models import Contact
        from tenant_apps.products.models import Product
        from tenant_apps.purchase_orders.models import PurchaseOrder
        from tenant_apps.sales_orders.models import SalesOrder
        from tenant_apps.invoices.models import Invoice
        from tenant_apps.accounts_receivables.models import AccountsReceivable
        from tenant_apps.carriers.models import Carrier
        from tenant_apps.plants.models import Plant
        
        # Models that guest user should have access to
        tenant_models = [
            Customer,
            Supplier,
            Contact,
            Product,
            PurchaseOrder,
            SalesOrder,
            Invoice,
            AccountsReceivable,
            Carrier,
            Plant,
        ]
        
        permissions_granted = 0
        
        for model in tenant_models:
            content_type = ContentType.objects.get_for_model(model)
            
            # Get all permissions for this model (view, add, change, delete)
            model_permissions = Permission.objects.filter(content_type=content_type)
            
            for perm in model_permissions:
                user.user_permissions.add(perm)
                permissions_granted += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Granted {permissions_granted} permissions for tenant-scoped models'
            )
        )
