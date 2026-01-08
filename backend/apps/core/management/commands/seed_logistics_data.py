"""
Management command to seed logistics data for testing.

Creates sample Tenants, Locations, Suppliers, Customers, Products, and Orders
based on Excel spreadsheet examples.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from apps.tenants.models import Tenant
from apps.core.models import Protein
from tenant_apps.locations.models import Location
from tenant_apps.suppliers.models import Supplier
from tenant_apps.customers.models import Customer
from tenant_apps.products.models import Product
from tenant_apps.carriers.models import Carrier
from tenant_apps.purchase_orders.models import PurchaseOrder, CarrierPurchaseOrder
from tenant_apps.sales_orders.models import SalesOrder
from tenant_apps.invoices.models import Invoice


class Command(BaseCommand):
    help = 'Seeds logistics data for testing (Tenants, Locations, Suppliers, Customers, Products, Orders)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seed data before creating new data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting seed data creation...'))

        with transaction.atomic():
            if options['clear']:
                self.stdout.write(self.style.WARNING('Clearing existing seed data...'))
                self._clear_data()

            # Create test tenant
            tenant = self._create_tenant()
            
            # Create proteins
            proteins = self._create_proteins()
            
            # Create locations
            locations = self._create_locations(tenant)
            
            # Create suppliers
            suppliers = self._create_suppliers(tenant, proteins, locations)
            
            # Create customers
            customers = self._create_customers(tenant, proteins, locations)
            
            # Create carriers
            carriers = self._create_carriers(tenant)
            
            # Create products
            products = self._create_products(tenant, suppliers)
            
            # Create purchase orders
            purchase_orders = self._create_purchase_orders(tenant, suppliers, products, locations, carriers)
            
            # Create sales orders
            sales_orders = self._create_sales_orders(tenant, suppliers, customers, products, locations, carriers)
            
            # Create invoices
            self._create_invoices(tenant, customers, sales_orders, products)

        self.stdout.write(self.style.SUCCESS('Successfully seeded logistics data!'))
        self.stdout.write(f'Tenant: {tenant.name}')
        self.stdout.write(f'Locations: {len(locations)}')
        self.stdout.write(f'Suppliers: {len(suppliers)}')
        self.stdout.write(f'Customers: {len(customers)}')
        self.stdout.write(f'Carriers: {len(carriers)}')
        self.stdout.write(f'Products: {len(products)}')
        self.stdout.write(f'Purchase Orders: {len(purchase_orders)}')
        self.stdout.write(f'Sales Orders: {len(sales_orders)}')

    def _clear_data(self):
        """Clear existing seed data."""
        Invoice.objects.filter(invoice_number__startswith='SEED-INV-').delete()
        SalesOrder.objects.filter(our_sales_order_num__startswith='SEED-SO-').delete()
        CarrierPurchaseOrder.objects.filter(our_carrier_po_num__startswith='SEED-CPO-').delete()
        PurchaseOrder.objects.filter(order_number__startswith='SEED-PO-').delete()
        Product.objects.filter(product_code__startswith='SEED-').delete()
        Carrier.objects.filter(code__startswith='SEED-').delete()
        Customer.objects.filter(name__startswith='SEED Customer').delete()
        Supplier.objects.filter(name__startswith='SEED').delete()
        Location.objects.filter(name__startswith='SEED').delete()
        Tenant.objects.filter(name='Seed Test Tenant').delete()

    def _create_tenant(self):
        """Create or get test tenant."""
        tenant, created = Tenant.objects.get_or_create(
            name='Seed Test Tenant',
            defaults={
                'slug': 'seed-test',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created tenant: {tenant.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing tenant: {tenant.name}'))
        return tenant

    def _create_proteins(self):
        """Create or get protein types."""
        proteins = {}
        protein_names = ['Beef', 'Pork', 'Chicken', 'Lamb', 'Turkey']
        
        for name in protein_names:
            protein, created = Protein.objects.get_or_create(name=name)
            proteins[name] = protein
            if created:
                self.stdout.write(f'  Created protein: {name}')
        
        return proteins

    def _create_locations(self, tenant):
        """Create sample locations."""
        locations = []
        
        location_data = [
            {
                'name': 'SEED JBS Plant - Grand Island, NE',
                'address': '2800 W Old Potash Hwy',
                'city': 'Grand Island',
                'state_zip': 'NE 68803',
                'contact_name': 'John Doe',
                'contact_phone': '308-555-0100',
                'contact_email': 'john.doe@jbs.com',
                'how_make_appointment': 'Email',
                'plant_est_number': 'EST-001',
            },
            {
                'name': 'SEED Customer Warehouse - Chicago, IL',
                'address': '1234 Warehouse Blvd',
                'city': 'Chicago',
                'state_zip': 'IL 60601',
                'contact_name': 'Jane Smith',
                'contact_phone': '312-555-0200',
                'contact_email': 'jane.smith@customer.com',
                'how_make_appointment': 'Phone',
                'plant_est_number': 'EST-002',
            },
            {
                'name': 'SEED Distribution Center - Dallas, TX',
                'address': '5678 Commerce St',
                'city': 'Dallas',
                'state_zip': 'TX 75201',
                'contact_name': 'Bob Johnson',
                'contact_phone': '214-555-0300',
                'contact_email': 'bob.johnson@distribution.com',
                'how_make_appointment': 'Website',
                'plant_est_number': 'EST-003',
            },
        ]
        
        for data in location_data:
            location, created = Location.objects.get_or_create(
                tenant=tenant,
                name=data['name'],
                defaults=data
            )
            locations.append(location)
            if created:
                self.stdout.write(f'  Created location: {location.name}')
        
        return locations

    def _create_suppliers(self, tenant, proteins, locations):
        """Create sample suppliers."""
        suppliers = []
        
        supplier_data = [
            {
                'name': 'SEED JBS USA',
                'contact_person': 'Michael Brown',
                'email': 'michael.brown@jbs.com',
                'phone': '970-555-0100',
                'city': 'Greeley',
                'state': 'CO',
                'country': 'USA',
                'origin': 'Domestic',
                'type_of_plant': 'Vertical',
                'type_of_certificate': 'BRC',
                'tested_product': True,
                'shipping_offered': 'Yes - Domestic',
                'departments_array': ['Sales', "Doc's BOL", "Doc's COA"],
                'accounting_payment_terms': 'Wire',
                'credit_limits': 'Net 30',
            },
            {
                'name': 'SEED Tyson Foods',
                'contact_person': 'Sarah Wilson',
                'email': 'sarah.wilson@tyson.com',
                'phone': '479-555-0200',
                'city': 'Springdale',
                'state': 'AR',
                'country': 'USA',
                'origin': 'Domestic',
                'type_of_plant': 'Processor',
                'type_of_certificate': 'SQF',
                'tested_product': True,
                'shipping_offered': 'Yes - Domestic & Exported',
                'departments_array': ['Sales', 'Accounting'],
                'accounting_payment_terms': 'ACH',
                'credit_limits': 'Net 45',
            },
        ]
        
        for data in supplier_data:
            supplier, created = Supplier.objects.get_or_create(
                tenant=tenant,
                name=data['name'],
                defaults=data
            )
            
            if created:
                # Add proteins
                supplier.proteins.add(proteins['Beef'], proteins['Pork'])
                # Link first location
                locations[0].supplier = supplier
                locations[0].save()
                
                self.stdout.write(f'  Created supplier: {supplier.name}')
            
            suppliers.append(supplier)
        
        return suppliers

    def _create_customers(self, tenant, proteins, locations):
        """Create sample customers."""
        customers = []
        
        customer_data = [
            {
                'name': 'SEED Customer - Sysco Foods',
                'contact_person': 'David Lee',
                'email': 'david.lee@sysco.com',
                'phone': '281-555-0300',
                'city': 'Houston',
                'state': 'TX',
                'country': 'USA',
                'industry_array': ['Food Service', 'Wholesaler'],
                'preferred_protein_types': ['Beef', 'Chicken', 'Pork'],
                'buyer_contact_name': 'Emily Davis',
                'buyer_contact_phone': '281-555-0301',
                'buyer_contact_email': 'emily.davis@sysco.com',
                'accounting_payment_terms': 'ACH',
                'credit_limits': 'Net 30',
            },
            {
                'name': 'SEED Customer - Restaurant Brands',
                'contact_person': 'Robert Martinez',
                'email': 'robert.martinez@restaurant.com',
                'phone': '305-555-0400',
                'city': 'Miami',
                'state': 'FL',
                'country': 'USA',
                'industry_array': ['Food Service'],
                'preferred_protein_types': ['Chicken', 'Beef'],
                'buyer_contact_name': 'Lisa Anderson',
                'buyer_contact_phone': '305-555-0401',
                'buyer_contact_email': 'lisa.anderson@restaurant.com',
                'accounting_payment_terms': 'Credit Card',
                'credit_limits': 'Net 15',
            },
        ]
        
        for data in customer_data:
            customer, created = Customer.objects.get_or_create(
                tenant=tenant,
                name=data['name'],
                defaults=data
            )
            
            if created:
                # Add proteins
                customer.proteins.add(proteins['Beef'], proteins['Chicken'])
                # Link second location
                if len(locations) > 1:
                    locations[1].customer = customer
                    locations[1].save()
                
                self.stdout.write(f'  Created customer: {customer.name}')
            
            customers.append(customer)
        
        return customers

    def _create_carriers(self, tenant):
        """Create sample carriers."""
        carriers = []
        
        carrier_data = [
            {
                'name': 'SEED Swift Transportation',
                'code': 'SEED-SWIFT',
                'carrier_type': 'truck',
                'contact_person': 'Thomas Clark',
                'phone': '602-555-0500',
                'email': 'thomas.clark@swift.com',
                'city': 'Phoenix',
                'state': 'AZ',
                'mc_number': 'MC123456',
                'dot_number': 'DOT789012',
                'departments_array': ['BOL', 'COA', 'POD'],
                'accounting_payment_terms': 'Wire',
                'credit_limits': 'Net 7',
                'how_carrier_make_appointment': 'Email',
            },
        ]
        
        for data in carrier_data:
            carrier, created = Carrier.objects.get_or_create(
                tenant=tenant,
                code=data['code'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created carrier: {carrier.name}')
            
            carriers.append(carrier)
        
        return carriers

    def _create_products(self, tenant, suppliers):
        """Create sample products."""
        products = []
        
        product_data = [
            {
                'product_code': 'SEED-BEEF-001',
                'description_of_product_item': '50% Lean Beef Trim - Frozen - Tested',
                'type_of_protein': 'Beef',
                'fresh_or_frozen': 'Frozen',
                'package_type': 'Boxed wax lined',
                'net_or_catch': 'Net',
                'edible_or_inedible': 'Edible',
                'tested_product': True,
                'supplier': suppliers[0] if suppliers else None,
                'origin': 'Domestic',
                'carton_type': 'Waxed Lined',
                'pcs_per_carton': '4/10',
                'uom': 'LB',
                'unit_weight': Decimal('2000.00'),
            },
            {
                'product_code': 'SEED-PORK-001',
                'description_of_product_item': 'Pork Shoulder Butt - Fresh',
                'type_of_protein': 'Pork',
                'fresh_or_frozen': 'Fresh',
                'package_type': 'Combo bins',
                'net_or_catch': 'Catch',
                'edible_or_inedible': 'Edible',
                'tested_product': False,
                'supplier': suppliers[1] if len(suppliers) > 1 else suppliers[0],
                'origin': 'Domestic',
                'carton_type': 'Plastic',
                'pcs_per_carton': '1',
                'uom': 'LB',
                'unit_weight': Decimal('1500.00'),
            },
        ]
        
        for data in product_data:
            product, created = Product.objects.get_or_create(
                tenant=tenant,
                product_code=data['product_code'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created product: {product.product_code}')
            
            products.append(product)
        
        return products

    def _create_purchase_orders(self, tenant, suppliers, products, locations, carriers):
        """Create sample purchase orders."""
        purchase_orders = []
        
        today = timezone.now().date()
        
        po_data = [
            {
                'order_number': 'SEED-PO-001',
                'supplier': suppliers[0] if suppliers else None,
                'product': products[0] if products else None,
                'order_date': today,
                'delivery_date': today + timedelta(days=7),
                'pick_up_date': today + timedelta(days=1),
                'total_amount': Decimal('50000.00'),
                'status': 'pending',
                'logistics_scenario': 'supplier_delivery',
                'quantity': 50,
                'total_weight': Decimal('100000.00'),
                'weight_unit': 'LBS',
                'price_per_unit': Decimal('1.00'),
                'type_of_protein': 'Beef',
                'fresh_or_frozen': 'Frozen',
                'package_type': 'Boxed wax lined',
                'payment_terms': 'Wire',
                'credit_limit': 'Net 30',
                'pick_up_location': locations[0] if locations else None,
                'delivery_location': locations[1] if len(locations) > 1 else None,
                'carrier': carriers[0] if carriers else None,
                'carrier_release_format': 'Supplier Confirmation Order Number',
            },
        ]
        
        for data in po_data:
            po, created = PurchaseOrder.objects.get_or_create(
                tenant=tenant,
                order_number=data['order_number'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created purchase order: {po.order_number}')
            
            purchase_orders.append(po)
        
        return purchase_orders

    def _create_sales_orders(self, tenant, suppliers, customers, products, locations, carriers):
        """Create sample sales orders."""
        sales_orders = []
        
        today = timezone.now().date()
        
        so_data = [
            {
                'our_sales_order_num': 'SEED-SO-001',
                'supplier': suppliers[0] if suppliers else None,
                'customer': customers[0] if customers else None,
                'product': products[0] if products else None,
                'pick_up_date': today + timedelta(days=2),
                'delivery_date': today + timedelta(days=8),
                'quantity': 30,
                'total_weight': Decimal('60000.00'),
                'weight_unit': 'LBS',
                'total_amount': Decimal('75000.00'),
                'status': 'pending',
                'pick_up_location': locations[0] if locations else None,
                'delivery_location': locations[1] if len(locations) > 1 else None,
                'carrier': carriers[0] if carriers else None,
                'carrier_release_format': 'Carrier Release Number',
                'plant_est_number': 'EST-001',
            },
        ]
        
        for data in so_data:
            so, created = SalesOrder.objects.get_or_create(
                tenant=tenant,
                our_sales_order_num=data['our_sales_order_num'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created sales order: {so.our_sales_order_num}')
            
            sales_orders.append(so)
        
        return sales_orders

    def _create_invoices(self, tenant, customers, sales_orders, products):
        """Create sample invoices."""
        today = timezone.now().date()
        
        invoice_data = [
            {
                'invoice_number': 'SEED-INV-001',
                'customer': customers[0] if customers else None,
                'sales_order': sales_orders[0] if sales_orders else None,
                'product': products[0] if products else None,
                'pick_up_date': today + timedelta(days=2),
                'delivery_date': today + timedelta(days=8),
                'due_date': today + timedelta(days=38),
                'our_sales_order_num': 'SEED-SO-001',
                'type_of_protein': 'Beef',
                'quantity': 30,
                'total_weight': Decimal('60000.00'),
                'weight_unit': 'LBS',
                'unit_price': Decimal('2.50'),
                'total_amount': Decimal('75000.00'),
                'status': 'sent',
                'payment_terms': 'ACH',
            },
        ]
        
        for data in invoice_data:
            invoice, created = Invoice.objects.get_or_create(
                tenant=tenant,
                invoice_number=data['invoice_number'],
                defaults=data
            )
            
            if created:
                self.stdout.write(f'  Created invoice: {invoice.invoice_number}')
