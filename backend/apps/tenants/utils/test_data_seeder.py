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
    Generate dummy business data for a tenant.
    
    Args:
        tenant: Tenant instance
        user: User to assign as owner/creator
        verbosity: Output verbosity level
    """
    try:
        # Import models dynamically to avoid circular dependencies
        from apps.core.models import Protein
        
        # Ensure Proteins exist (Global/Shared model)
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
    
    # Create Suppliers
    try:
        from tenant_apps.suppliers.models import Supplier
        
        for i in range(1, 4):
            Supplier.objects.get_or_create(
                tenant=tenant,
                code=f"SUP-{i:03d}",
                defaults={
                    'name': f"Supplier {i} - {tenant.name}",
                    'status': 'active',
                    'owner': user,
                    'created_by': user,
                    'modified_by': user
                }
            )
        
        if verbosity >= 2:
            print(f"  🏭 Created 3 suppliers")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Supplier model not available: {e}")
    
    # Create Customers
    try:
        from tenant_apps.customers.models import Customer
        
        for i in range(1, 4):
            Customer.objects.get_or_create(
                tenant=tenant,
                code=f"CUST-{i:03d}",
                defaults={
                    'name': f"Customer {i} - {tenant.name}",
                    'status': 'active',
                    'owner': user,
                    'created_by': user,
                    'modified_by': user
                }
            )
        
        if verbosity >= 2:
            print(f"  👥 Created 3 customers")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Customer model not available: {e}")
    
    # Create Products
    try:
        from tenant_apps.products.models import Product
        
        for i in range(1, 4):
            Product.objects.get_or_create(
                tenant=tenant,
                code=f"PROD-{i:03d}",
                defaults={
                    'name': f"Product {i}",
                    'protein_type': random.choice(protein_objs) if protein_objs else None,
                    'status': 'active',
                    'owner': user,
                    'created_by': user,
                    'modified_by': user
                }
            )
        
        if verbosity >= 2:
            print(f"  📦 Created 3 products")
            
    except ImportError as e:
        if verbosity >= 1:
            print(f"  ⚠️  Product model not available: {e}")
