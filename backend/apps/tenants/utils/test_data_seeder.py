"""
Utility for generating comprehensive test data for development/UAT.
Creates tenants, users, and business data (products, suppliers, etc.).
"""
import random
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from apps.tenants.models import Tenant, TenantUser, TenantDomain


def seed_test_data(environment='development', count=3, verbosity=1):
    """
    Orchestrate the creation of test tenants and their data.
    Returns a list of created Tenant objects with attached 'test_credentials' dict.
    
    Args:
        environment: Environment name (development, uat, etc.)
        count: Number of test tenants to create
        verbosity: Output verbosity level (0=silent, 1=normal, 2=verbose)
    
    Returns:
        List of Tenant objects with test_credentials attribute
    """
    
    # 1. Cleanup existing test data for this environment
    prefix = f"test_{environment}"
    existing = Tenant.objects.filter(schema_name__startswith=prefix)
    if verbosity >= 1:
        print(f"🗑️  Cleaning up {existing.count()} existing test tenants...")
    existing.delete()
    
    created_tenants = []
    
    # 2. Create new test data
    for i in range(1, count + 1):
        schema_name = f"{prefix}_{i}"
        tenant_name = f"Test Company {i} ({environment.title()})"
        slug = schema_name.replace('_', '-')
        
        with transaction.atomic():
            # Create Tenant
            tenant = Tenant.objects.create(
                name=tenant_name,
                slug=slug,
                schema_name=schema_name,
                domain=None,  # Will be set by TenantDomain
                contact_email=f"contact@{slug}.com",
                is_active=True,
                is_trial=True,
                trial_ends_at=timezone.now() + timezone.timedelta(days=30)
            )
            
            # Create Domain
            TenantDomain.objects.create(
                tenant=tenant,
                domain=f"{slug}.localhost",
                is_primary=True
            )
            
            # Create Admin User
            admin_username = f"admin_{schema_name}"
            admin_email = f"admin@{schema_name}.com"
            admin_password = "password123!"  # Standard test password
            
            user, created = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    'email': admin_email,
                    'first_name': 'Admin',
                    'last_name': f'Test {i}',
                    'is_staff': True,  # Allow admin access
                }
            )
            if created:
                user.set_password(admin_password)
                user.save()
            
            # Link User to Tenant
            TenantUser.objects.get_or_create(
                tenant=tenant,
                user=user,
                defaults={
                    'role': 'admin',
                    'is_active': True
                }
            )
            
            # Populate Business Data
            _populate_tenant_business_data(tenant, user, verbosity)
            
            # Attach credentials for display
            tenant.test_credentials = {
                'username': admin_username,
                'password': admin_password,
                'role': 'Admin'
            }
            created_tenants.append(tenant)
            
            if verbosity >= 1:
                print(f"✅ Created {tenant.name} with admin {admin_username}")
                
    return created_tenants


def _populate_tenant_business_data(tenant, user, verbosity=1):
    """
    Generate dummy business data for a tenant with strict dependency ordering.
    
    CRITICAL EXECUTION ORDER:
    1. Protein (Global/Shared)
    2. Plant (tenant-isolated)
    3. Contact (tenant-isolated)
    4. Carrier (tenant-isolated)
    5. Supplier (depends on Plant, Contact)
    6. Customer (depends on Plant, Contact)
    7. Product (depends on Supplier)
    8. PurchaseOrder (depends on Supplier, Carrier, Plant, Contact)
    
    Args:
        tenant: Tenant instance
        user: User to assign as owner/creator
        verbosity: Output verbosity level
    """
    # === STEP 1: Ensure Proteins exist (Global/Shared model) ===
    try:
        from apps.core.models import Protein
        
        proteins = ['Beef', 'Pork', 'Chicken', 'Lamb', 'Turkey']
        protein_objs = []
        for p_name in proteins:
            p, _ = Protein.objects.get_or_create(name=p_name)
            protein_objs.append(p)
        
        if verbosity >= 2:
            print(f"  📦 Created/verified {len(protein_objs)} protein types")
        
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Could not import Protein model: {e}")
        protein_objs = []
    
    # === STEP 2: Create Plants (tenant-isolated) ===
    plants = []
    try:
        from tenant_apps.plants.models import Plant
        
        for i in range(1, 4):
            plant, _ = Plant.objects.get_or_create(
                tenant=tenant,
                code=f"PLT-{tenant.slug}-{i}",  # Globally unique
                defaults={
                    'name': f"Plant {i} - {tenant.name}",
                    'plant_type': 'processing',
                    'address': f"{i}00 Industrial Blvd",
                    'city': f"City {i}",
                    'state': 'TX',
                    'zip_code': f"7500{i}",
                    'country': 'USA',
                    'phone': f"555-010{i}",
                    'email': f"plant{i}@{tenant.slug}.example.com",
                    'manager': f"Manager {i}",
                    'capacity': 1000 * i,
                    'is_active': True,
                    'created_by': user
                }
            )
            plants.append(plant)
        
        if verbosity >= 2:
            print(f"  🏭 Created 3 plants")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Plant model not available: {e}")
    
    # === STEP 3: Create Contacts (tenant-isolated) ===
    contacts = []
    try:
        from tenant_apps.contacts.models import Contact
        
        for i in range(1, 4):
            contact, _ = Contact.objects.get_or_create(
                tenant=tenant,
                email=f"contact{i}@{tenant.schema_name}.com",
                defaults={
                    'first_name': f"Contact{i}",
                    'last_name': f"Test",
                    'phone': f"555-010{i}",
                    'status': 'active',
                    'company': f"Company {i}",
                    'position': f"Manager {i}",
                    'contact_type': 'general'
                }
            )
            contacts.append(contact)
        
        if verbosity >= 2:
            print(f"  👤 Created 3 contacts")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Contact model not available: {e}")
    
    # === STEP 4: Create Carriers (tenant-isolated) ===
    carriers = []
    try:
        from tenant_apps.carriers.models import Carrier
        
        for i in range(1, 4):
            carrier, _ = Carrier.objects.get_or_create(
                tenant=tenant,
                code=f"CARR-{tenant.slug}-{i}",  # Globally unique
                defaults={
                    'name': f"Carrier {i} - {tenant.name}",
                    'carrier_type': 'truck',
                    'contact_person': f"Driver {i}",
                    'phone': f"555-020{i}",
                    'email': f"carrier{i}@example.com",
                    'address': f"{i}00 Highway Rd",
                    'city': f"City {i}",
                    'state': 'TX',
                    'zip_code': f"7600{i}",
                    'country': 'USA',
                    'is_active': True,
                    'created_by': user
                }
            )
            carriers.append(carrier)
        
        if verbosity >= 2:
            print(f"  🚚 Created 3 carriers")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Carrier model not available: {e}")
    
    # === STEP 5: Create Suppliers (depends on Plant, Contact) ===
    suppliers = []
    try:
        from tenant_apps.suppliers.models import Supplier
        
        for i in range(1, 4):
            supplier_defaults = {
                'name': f"Supplier {i} - {tenant.name}",
                'contact_person': f"Supplier Contact {i}",
                'email': f"supplier{i}@{tenant.slug}.example.com",
                'phone': f"555-030{i}",
                'address': f"{i}00 Supplier Ave",
                'city': f"City {i}",
                'state': 'TX',
                'zip_code': f"7700{i}",
                'country': 'USA'
            }
            
            # Assign random Plant if available
            if plants:
                supplier_defaults['plant'] = random.choice(plants)
            
            supplier, _ = Supplier.objects.get_or_create(
                tenant=tenant,
                name=f"Supplier {i} - {tenant.name}",  # Use name as unique identifier
                defaults=supplier_defaults
            )
            suppliers.append(supplier)
            
            # Add contacts via ManyToMany relationship after creation
            if contacts:
                supplier.contacts.add(random.choice(contacts))
        
        if verbosity >= 2:
            print(f"  🏭 Created 3 suppliers")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Supplier model not available: {e}")
    
    # === STEP 6: Create Customers (depends on Plant, Contact) ===
    try:
        from tenant_apps.customers.models import Customer
        
        for i in range(1, 4):
            customer_defaults = {
                'name': f"Customer {i} - {tenant.name}",
                'contact_person': f"Customer Contact {i}",
                'email': f"customer{i}@{tenant.slug}.example.com",
                'phone': f"555-040{i}",
                'address': f"{i}00 Customer St",
                'city': f"City {i}",
                'state': 'TX',
                'zip_code': f"7800{i}",
                'country': 'USA'
            }
            
            # Assign random Plant if available
            if plants:
                customer_defaults['plant'] = random.choice(plants)
            
            customer, _ = Customer.objects.get_or_create(
                tenant=tenant,
                name=f"Customer {i} - {tenant.name}",  # Use name as unique identifier
                defaults=customer_defaults
            )
            
            # Add contacts via ManyToMany relationship after creation
            if contacts:
                customer.contacts.add(random.choice(contacts))
        
        if verbosity >= 2:
            print(f"  👥 Created 3 customers")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Customer model not available: {e}")
    
    # === STEP 7: Create Products (depends on Supplier, Protein) ===
    try:
        from tenant_apps.products.models import Product
        
        for i in range(1, 4):
            product_defaults = {
                'description_of_product_item': f"Test Product {i} - {tenant.name}",
                'fresh_or_frozen': 'fresh',
                'package_type': 'box',
                'net_or_catch': 'net',
                'is_active': True
            }
            
            # Assign random Protein if available (type_of_protein is CharField, not FK)
            if protein_objs:
                product_defaults['type_of_protein'] = random.choice(['beef', 'pork', 'chicken', 'turkey'])
            
            Product.objects.get_or_create(
                tenant=tenant,
                product_code=f"PROD-{tenant.slug}-{i}",  # Globally unique
                defaults=product_defaults
            )
        
        if verbosity >= 2:
            print(f"  📦 Created 3 products")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Product model not available: {e}")
    
    # === STEP 8: Create PurchaseOrders (depends on Supplier, Carrier, Plant, Contact) ===
    try:
        from tenant_apps.purchase_orders.models import PurchaseOrder
        from decimal import Decimal
        
        for i in range(1, 4):
            po_defaults = {
                'status': 'pending',
                'order_date': timezone.now().date(),
                'pick_up_date': timezone.now().date(),
                'total_amount': Decimal('1000.00') * i,
                'quantity': 100 * i,
                'total_weight': Decimal('500.00') * i,
                'weight_unit': 'lbs'
            }
            
            # Assign random related objects if available
            if suppliers:
                po_defaults['supplier'] = random.choice(suppliers)
            if carriers:
                po_defaults['carrier'] = random.choice(carriers)
            
            PurchaseOrder.objects.get_or_create(
                tenant=tenant,
                order_number=f"PO-{tenant.slug}-{i:04d}",  # Globally unique
                defaults=po_defaults
            )
        
        if verbosity >= 2:
            print(f"  📝 Created 3 purchase orders")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  PurchaseOrder model not available: {e}")
