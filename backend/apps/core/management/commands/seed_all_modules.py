"""
Management command to seed all ERP modules with realistic data.

Usage:
    python manage.py seed_all_modules
    python manage.py seed_all_modules --tenant-id=1
    python manage.py seed_all_modules --clear  # Clear existing data first
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import random

from apps.tenants.models import Tenant
from tenant_apps.suppliers.models import Supplier
from tenant_apps.customers.models import Customer
from tenant_apps.plants.models import Plant
from tenant_apps.carriers.models import Carrier
from tenant_apps.products.models import Product
from tenant_apps.purchase_orders.models import PurchaseOrder
from tenant_apps.sales_orders.models import SalesOrder
from tenant_apps.invoices.models import Invoice, Claim
from tenant_apps.cockpit.models import ActivityLog, ScheduledCall
from tenant_apps.contacts.models import Contact


class Command(BaseCommand):
    help = 'Seeds all ERP modules with realistic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='Specific tenant ID to seed (default: first tenant)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of records to create per model (default: 10)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting ERP module seeding...'))

        # Get tenant
        tenant_id = options.get('tenant_id')
        if tenant_id:
            tenant = Tenant.objects.get(id=tenant_id)
        else:
            # Try to use "Seed Test Tenant" which has logistics data
            try:
                tenant = Tenant.objects.get(name='Seed Test Tenant')
            except Tenant.DoesNotExist:
                tenant = Tenant.objects.first()
            
            if not tenant:
                self.stdout.write(self.style.ERROR('❌ No tenants found. Run seed_tenants first.'))
                return

        self.stdout.write(f'📍 Using tenant: {tenant.name} (ID: {tenant.id})')

        # Get or create user
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='admin',
                email='admin@meatscentral.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Created admin user'))

        count = options.get('count', 10)

        # Clear if requested
        if options.get('clear'):
            self.stdout.write(self.style.WARNING('🗑️  Clearing existing data...'))
            self._clear_data(tenant)

        # Seed in order (respecting dependencies)
        # Skip carriers/contacts - they may already exist from seed_logistics_data
        self.stdout.write('ℹ️  Skipping Carriers/Contacts (assumed to exist from seed_logistics_data)')
        
        # Only seed the new models we created
        self.seed_claims(tenant, user, count=int(count * 0.5))  # Half the count for claims
        self.seed_activity_logs(tenant, user, count=count)
        self.seed_scheduled_calls(tenant, user, count=int(count * 0.3))  # Fewer scheduled calls

        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'🎉 Created data for tenant: {tenant.name}'))

    def _clear_data(self, tenant):
        """Clear all seeded data for the tenant."""
        ScheduledCall.objects.filter(tenant=tenant).delete()
        ActivityLog.objects.filter(tenant=tenant).delete()
        Claim.objects.filter(tenant=tenant).delete()
        Invoice.objects.filter(tenant=tenant).delete()
        SalesOrder.objects.filter(tenant=tenant).delete()
        # Don't delete PurchaseOrders, Suppliers, Customers - they may have real data

    def seed_plants(self, tenant, count=5):
        """Seed plant/facility data."""
        self.stdout.write('🏭 Seeding Plants...')
        
        suppliers = Supplier.objects.filter(tenant=tenant)[:3]
        if not suppliers:
            self.stdout.write(self.style.WARNING('  ⚠️  No suppliers found, skipping plants'))
            return

        plant_names = [
            'North Processing Facility',
            'South Distribution Center',
            'East Warehouse Complex',
            'West Cold Storage',
            'Central Packaging Plant',
        ]

        for i, name in enumerate(plant_names[:count]):
            plant, created = Plant.objects.get_or_create(
                tenant=tenant,
                code=f'PLT-{i+1:03d}',
                defaults={
                    'name': name,
                    'plant_est_num': f'EST{1000 + i}',
                    'plant_type': random.choice(['processing', 'distribution', 'warehouse']),
                    'address': f'{100 + i*10} Industrial Blvd',
                    'city': random.choice(['Dallas', 'Houston', 'Austin', 'San Antonio']),
                    'state': 'TX',
                    'zip_code': f'75{i:03d}',
                    'phone': f'214-555-{i:04d}',
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created plant: {plant.name}')

    def seed_carriers(self, tenant, count=3):
        """Seed carrier/logistics companies."""
        self.stdout.write('🚛 Seeding Carriers...')
        
        carrier_names = [
            'Swift Logistics LLC',
            'MeatHaul Express',
            'ColdChain Freight Co',
        ]

        for i, name in enumerate(carrier_names[:count]):
            carrier, created = Carrier.objects.get_or_create(
                tenant=tenant,
                code=f'CAR-{i+1:03d}',  # Added required code field
                defaults={
                    'name': name,
                    'dot_number': f'DOT{100000 + i}',
                    'mc_number': f'MC{200000 + i}',
                    'contact_person': f'Dispatcher {i+1}',
                    'phone': f'800-555-{i:04d}',
                    'email': f'dispatch{i+1}@carrier{i+1}.com',
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created carrier: {carrier.name}')

    def seed_contacts(self, tenant, count=15):
        """Seed contact persons."""
        self.stdout.write('📞 Seeding Contacts...')
        
        first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'James', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
        
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            
            contact, created = Contact.objects.get_or_create(
                tenant=tenant,
                email=f'{first.lower()}.{last.lower()}{i}@example.com',
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': f'214-555-{i:04d}',
                }
            )
            if created and i < 3:  # Only show first few
                self.stdout.write(f'  ✓ Created contact: {contact.first_name} {contact.last_name}')
        
        self.stdout.write(f'  ✓ Created {count} contacts')

    def seed_products(self, tenant, count=8):
        """Seed product data."""
        self.stdout.write('🥩 Seeding Products...')
        
        products = [
            ('80/20 Beef Trim', 'Beef', 'fresh', 'combo'),
            ('90/10 Beef Trim', 'Beef', 'fresh', 'combo'),
            ('Boneless Pork Shoulder', 'Pork', 'frozen', 'box'),
            ('Chicken Breast IQF', 'Chicken', 'frozen', 'box'),
            ('Beef Tongue', 'Beef', 'fresh', 'combo'),
            ('Pork Belly', 'Pork', 'frozen', 'box'),
            ('Ground Turkey', 'Chicken', 'fresh', 'box'),
            ('Beef Short Ribs', 'Beef', 'frozen', 'box'),
        ]

        for i, (name, protein, state, pkg) in enumerate(products[:count]):
            product, created = Product.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'sku': f'SKU-{i+1:04d}',
                    'description': f'{state.title()} {protein} product',
                    'protein_type': protein.lower(),
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created product: {product.name}')

    def seed_sales_orders(self, tenant, user, count=10):
        """Seed sales order data."""
        self.stdout.write('📦 Seeding Sales Orders...')
        
        customers = Customer.objects.filter(tenant=tenant)
        suppliers = Supplier.objects.filter(tenant=tenant)
        products = Product.objects.filter(tenant=tenant)
        
        if not customers or not suppliers:
            self.stdout.write(self.style.WARNING('  ⚠️  No customers/suppliers found, skipping sales orders'))
            return

        statuses = ['pending', 'confirmed', 'in_transit', 'delivered']
        
        for i in range(count):
            so_num = f'SO-{timezone.now().year}-{i+1:04d}'
            
            so, created = SalesOrder.objects.get_or_create(
                tenant=tenant,
                our_sales_order_num=so_num,
                defaults={
                    'supplier': random.choice(suppliers),
                    'customer': random.choice(customers),
                    'product': random.choice(products) if products else None,
                    'status': random.choice(statuses),
                    'pick_up_date': date.today() + timedelta(days=random.randint(1, 30)),
                    'delivery_date': date.today() + timedelta(days=random.randint(31, 60)),
                    'quantity': random.randint(100, 1000),
                    'total_weight': Decimal(str(random.randint(1000, 50000))),
                    'total_amount': Decimal(str(random.randint(5000, 50000))),
                }
            )
            if created and i < 3:
                self.stdout.write(f'  ✓ Created sales order: {so.our_sales_order_num}')
        
        self.stdout.write(f'  ✓ Created {count} sales orders')

    def seed_invoices(self, tenant, count=10):
        """Seed invoice data."""
        self.stdout.write('🧾 Seeding Invoices...')
        
        customers = Customer.objects.filter(tenant=tenant)
        sales_orders = SalesOrder.objects.filter(tenant=tenant)
        
        if not customers:
            self.stdout.write(self.style.WARNING('  ⚠️  No customers found, skipping invoices'))
            return

        statuses = ['draft', 'sent', 'paid', 'overdue']
        
        for i in range(count):
            inv_num = f'INV-{timezone.now().year}-{i+1:04d}'
            
            inv, created = Invoice.objects.get_or_create(
                tenant=tenant,
                invoice_number=inv_num,
                defaults={
                    'customer': random.choice(customers),
                    'sales_order': random.choice(sales_orders) if sales_orders else None,
                    'status': random.choice(statuses),
                    'total_amount': Decimal(str(random.randint(1000, 25000))),
                    'due_date': date.today() + timedelta(days=random.choice([15, 30, 45, 60])),
                }
            )
            if created and i < 3:
                self.stdout.write(f'  ✓ Created invoice: {inv.invoice_number}')
        
        self.stdout.write(f'  ✓ Created {count} invoices')

    def seed_claims(self, tenant, user, count=5):
        """Seed claims data."""
        self.stdout.write('⚖️  Seeding Claims...')
        
        suppliers = Supplier.objects.filter(tenant=tenant)
        customers = Customer.objects.filter(tenant=tenant)
        pos = PurchaseOrder.objects.filter(tenant=tenant)
        sos = SalesOrder.objects.filter(tenant=tenant)
        
        if not suppliers or not customers:
            self.stdout.write(self.style.WARNING('  ⚠️  No suppliers/customers found, skipping claims'))
            return

        claim_reasons = [
            'Damaged product upon delivery',
            'Incorrect weight - short by 500 lbs',
            'Quality issue - product not meeting spec',
            'Late delivery causing customer complaint',
            'Incorrect product shipped',
        ]

        for i in range(count):
            claim_type = 'payable' if i % 2 == 0 else 'receivable'
            claim_num = f'CLM-{timezone.now().year}-{i+1:04d}'
            
            claim, created = Claim.objects.get_or_create(
                tenant=tenant,
                claim_number=claim_num,
                defaults={
                    'claim_type': claim_type,
                    'status': random.choice(['pending', 'approved', 'settled']),
                    'supplier': random.choice(suppliers) if claim_type == 'payable' else None,
                    'customer': random.choice(customers) if claim_type == 'receivable' else None,
                    'purchase_order': random.choice(pos) if pos and claim_type == 'payable' else None,
                    'sales_order': random.choice(sos) if sos and claim_type == 'receivable' else None,
                    'reason': random.choice(claim_reasons),
                    'claimed_amount': Decimal(str(random.randint(500, 5000))),
                    'claim_date': date.today() - timedelta(days=random.randint(1, 60)),
                    'created_by': user,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created claim: {claim.claim_number} ({claim.get_claim_type_display()})')

    def seed_activity_logs(self, tenant, user, count=20):
        """Seed activity log notes."""
        self.stdout.write('📝 Seeding Activity Logs...')
        
        suppliers = Supplier.objects.filter(tenant=tenant)
        customers = Customer.objects.filter(tenant=tenant)
        pos = PurchaseOrder.objects.filter(tenant=tenant)
        
        entities = []
        for supplier in suppliers[:3]:
            entities.append(('supplier', supplier.id, f'Supplier: {supplier.name}'))
        for customer in customers[:3]:
            entities.append(('customer', customer.id, f'Customer: {customer.name}'))
        for po in pos[:3]:
            entities.append(('purchase_order', po.id, f'PO: {po.order_number}'))

        if not entities:
            self.stdout.write(self.style.WARNING('  ⚠️  No entities found, skipping activity logs'))
            return

        note_templates = [
            'Called to confirm order details',
            'Discussed pricing for next month',
            'Reviewed quality concerns from last shipment',
            'Confirmed delivery schedule for next week',
            'Negotiated payment terms extension',
            'Followed up on pending documentation',
            'Discussed new product offerings',
            'Reviewed monthly performance metrics',
        ]

        for i in range(count):
            entity_type, entity_id, entity_name = random.choice(entities)
            
            # Don't set content_type/object_id - use entity_type/entity_id instead
            log = ActivityLog.objects.create(
                tenant=tenant,
                entity_type=entity_type,
                entity_id=entity_id,
                title=f'{random.choice(["Call Log", "Meeting Notes", "Follow-up", "Update"])}',
                content=random.choice(note_templates),
                created_by=user,
                is_pinned=(i % 10 == 0),  # Pin every 10th note
            )
            
            if i < 3:
                self.stdout.write(f'  ✓ Created activity log for {entity_name}')
        
        self.stdout.write(f'  ✓ Created {count} activity logs')

    def seed_scheduled_calls(self, tenant, user, count=5):
        """Seed scheduled calls."""
        self.stdout.write('📅 Seeding Scheduled Calls...')
        
        suppliers = Supplier.objects.filter(tenant=tenant)
        customers = Customer.objects.filter(tenant=tenant)
        
        entities = []
        for supplier in suppliers[:3]:
            entities.append(('supplier', supplier.id, supplier.name))
        for customer in customers[:3]:
            entities.append(('customer', customer.id, customer.name))

        if not entities:
            self.stdout.write(self.style.WARNING('  ⚠️  No entities found, skipping scheduled calls'))
            return

        for i in range(count):
            entity_type, entity_id, entity_name = random.choice(entities)
            
            scheduled_for = timezone.now() + timedelta(days=random.randint(1, 14), hours=random.randint(9, 16))
            
            call = ScheduledCall.objects.create(
                tenant=tenant,
                entity_type=entity_type,
                entity_id=entity_id,
                title=f'Follow-up call with {entity_name}',
                description=f'Discuss {random.choice(["pricing", "delivery schedule", "quality concerns", "new products"])}',
                scheduled_for=scheduled_for,
                duration_minutes=random.choice([15, 30, 45, 60]),
                is_completed=(i % 3 == 0),  # Complete every 3rd call
                assigned_to=user,
                created_by=user,
            )
            
            self.stdout.write(f'  ✓ Created scheduled call: {call.title}')
