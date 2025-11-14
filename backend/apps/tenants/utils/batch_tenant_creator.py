"""
Utility script for batch-creating demo/test tenants and domains.

This script provides functions to create multiple tenants for testing and demo purposes
across different environments (development, staging, UAT, production).

Usage:
    from apps.tenants.utils.batch_tenant_creator import create_demo_tenants
    
    # Create development demo tenants
    create_demo_tenants(environment='development')
    
    # Create custom tenants
    create_custom_tenants([
        {'schema_name': 'acme', 'name': 'ACME Corp', 'domain': 'acme.example.com'},
        {'schema_name': 'globex', 'name': 'Globex Inc', 'domain': 'globex.example.com'},
    ])
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from apps.tenants.models import Tenant, TenantDomain


def create_demo_tenants(
    environment: str = 'development',
    count: int = 3,
    verbosity: int = 1
) -> List[Tenant]:
    """
    Create demo/test tenants for a specific environment.
    
    Args:
        environment: Environment name ('development', 'staging', 'uat', 'production')
        count: Number of demo tenants to create
        verbosity: Output verbosity level (0=silent, 1=normal, 2=verbose)
    
    Returns:
        List of created Tenant objects
    
    Example:
        >>> from apps.tenants.utils.batch_tenant_creator import create_demo_tenants
        >>> tenants = create_demo_tenants(environment='development', count=5)
        >>> print(f'Created {len(tenants)} demo tenants')
    """
    if verbosity >= 1:
        print(f'\n🏢 Creating {count} demo tenants for {environment} environment...\n')
    
    tenants = []
    demo_configs = _get_demo_tenant_configs(environment, count)
    
    for config in demo_configs:
        try:
            tenant = create_single_tenant(
                schema_name=config['schema_name'],
                name=config['name'],
                slug=config.get('slug'),
                contact_email=config.get('contact_email'),
                contact_phone=config.get('contact_phone', ''),
                on_trial=config.get('on_trial', True),
                trial_ends_at=config.get('trial_ends_at'),
                domain=config.get('domain'),
                is_primary=config.get('is_primary', True),
                verbosity=verbosity,
            )
            tenants.append(tenant)
        except Exception as e:
            if verbosity >= 1:
                print(f'❌ Failed to create tenant {config["name"]}: {str(e)}')
    
    if verbosity >= 1:
        print(f'\n✅ Successfully created {len(tenants)} demo tenants\n')
    
    return tenants


def create_custom_tenants(
    tenant_configs: List[Dict],
    verbosity: int = 1
) -> List[Tenant]:
    """
    Create multiple tenants from custom configurations.
    
    Args:
        tenant_configs: List of tenant configuration dictionaries
        verbosity: Output verbosity level (0=silent, 1=normal, 2=verbose)
    
    Returns:
        List of created Tenant objects
    
    Example:
        >>> configs = [
        ...     {
        ...         'schema_name': 'acme_corp',
        ...         'name': 'ACME Corporation',
        ...         'domain': 'acme.example.com',
        ...         'contact_email': 'admin@acme.com',
        ...         'on_trial': False,
        ...     },
        ...     {
        ...         'schema_name': 'test_company',
        ...         'name': 'Test Company',
        ...         'domain': 'test.example.com',
        ...         'on_trial': True,
        ...     }
        ... ]
        >>> tenants = create_custom_tenants(configs)
    """
    if verbosity >= 1:
        print(f'\n🏢 Creating {len(tenant_configs)} custom tenants...\n')
    
    tenants = []
    
    for config in tenant_configs:
        try:
            tenant = create_single_tenant(
                schema_name=config['schema_name'],
                name=config['name'],
                slug=config.get('slug'),
                contact_email=config.get('contact_email'),
                contact_phone=config.get('contact_phone', ''),
                on_trial=config.get('on_trial', True),
                trial_ends_at=config.get('trial_ends_at'),
                domain=config.get('domain'),
                is_primary=config.get('is_primary', True),
                verbosity=verbosity,
            )
            tenants.append(tenant)
        except Exception as e:
            if verbosity >= 1:
                print(f'❌ Failed to create tenant {config["name"]}: {str(e)}')
    
    if verbosity >= 1:
        print(f'\n✅ Successfully created {len(tenants)} custom tenants\n')
    
    return tenants


def create_single_tenant(
    schema_name: str,
    name: str,
    slug: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_phone: str = '',
    on_trial: bool = True,
    trial_ends_at: Optional[datetime] = None,
    domain: Optional[str] = None,
    is_primary: bool = True,
    verbosity: int = 1,
) -> Tenant:
    """
    Create a single tenant with optional domain.
    
    Args:
        schema_name: Database schema name (unique identifier)
        name: Tenant organization name
        slug: URL-friendly identifier (auto-generated if not provided)
        contact_email: Primary contact email
        contact_phone: Primary contact phone
        on_trial: Whether tenant is on trial
        trial_ends_at: Trial end date (auto-set to 30 days if on_trial and not provided)
        domain: Domain name for tenant routing
        is_primary: Whether domain is primary
        verbosity: Output verbosity level
    
    Returns:
        Created Tenant object
    
    Raises:
        ValueError: If tenant with schema_name already exists
    """
    # Generate defaults
    if not slug:
        slug = schema_name.replace('_', '-')
    
    if not contact_email:
        contact_email = f'admin@{slug}.local'
    
    if on_trial and not trial_ends_at:
        trial_ends_at = timezone.now() + timedelta(days=30)
    
    # Check if tenant already exists
    if Tenant.objects.filter(schema_name=schema_name).exists():
        raise ValueError(f'Tenant with schema_name "{schema_name}" already exists')
    
    if Tenant.objects.filter(slug=slug).exists():
        raise ValueError(f'Tenant with slug "{slug}" already exists')
    
    try:
        with transaction.atomic():
            # Create tenant
            tenant = Tenant.objects.create(
                schema_name=schema_name,
                name=name,
                slug=slug,
                contact_email=contact_email,
                contact_phone=contact_phone,
                is_active=True,
                is_trial=on_trial,
                trial_ends_at=trial_ends_at,
            )
            
            if verbosity >= 1:
                print(f'✅ Created tenant: {tenant.name} ({tenant.schema_name})')
            
            # Create domain if provided
            if domain:
                domain_obj = TenantDomain.objects.create(
                    domain=domain.lower(),
                    tenant=tenant,
                    is_primary=is_primary,
                )
                
                if verbosity >= 1:
                    print(f'   ↳ Domain: {domain_obj.domain} {"(primary)" if is_primary else ""}')
            
            return tenant
            
    except Exception as e:
        if verbosity >= 1:
            print(f'❌ Error creating tenant {name}: {str(e)}')
        raise


def _get_demo_tenant_configs(environment: str, count: int) -> List[Dict]:
    """
    Generate demo tenant configurations for a specific environment.
    
    Args:
        environment: Environment name
        count: Number of configurations to generate
    
    Returns:
        List of tenant configuration dictionaries
    """
    configs = []
    
    # Base demo tenant data
    demo_companies = [
        {'name': 'ACME Corporation', 'schema': 'acme_corp', 'domain_suffix': 'acme'},
        {'name': 'Globex Inc', 'schema': 'globex_inc', 'domain_suffix': 'globex'},
        {'name': 'Initech LLC', 'schema': 'initech_llc', 'domain_suffix': 'initech'},
        {'name': 'Umbrella Corp', 'schema': 'umbrella_corp', 'domain_suffix': 'umbrella'},
        {'name': 'Soylent Industries', 'schema': 'soylent_ind', 'domain_suffix': 'soylent'},
        {'name': 'Stark Enterprises', 'schema': 'stark_ent', 'domain_suffix': 'stark'},
        {'name': 'Wayne Enterprises', 'schema': 'wayne_ent', 'domain_suffix': 'wayne'},
        {'name': 'Oscorp Industries', 'schema': 'oscorp_ind', 'domain_suffix': 'oscorp'},
        {'name': 'Massive Dynamic', 'schema': 'massive_dyn', 'domain_suffix': 'massive'},
        {'name': 'Cyberdyne Systems', 'schema': 'cyberdyne_sys', 'domain_suffix': 'cyberdyne'},
    ]
    
    # Environment-specific settings
    env_settings = {
        'development': {
            'domain_base': 'localhost',
            'trial_days': 30,
            'on_trial': True,
        },
        'staging': {
            'domain_base': 'staging.meatscentral.com',
            'trial_days': 60,
            'on_trial': True,
        },
        'uat': {
            'domain_base': 'uat.meatscentral.com',
            'trial_days': 90,
            'on_trial': True,
        },
        'production': {
            'domain_base': 'meatscentral.com',
            'trial_days': 30,
            'on_trial': False,
        },
    }
    
    settings = env_settings.get(environment, env_settings['development'])
    
    for i, company in enumerate(demo_companies[:count]):
        config = {
            'schema_name': f"{environment}_{company['schema']}",
            'name': f"{company['name']} ({environment.title()})",
            'slug': f"{environment}-{company['schema'].replace('_', '-')}",
            'contact_email': f"admin@{company['domain_suffix']}.{settings['domain_base']}",
            'contact_phone': f'+1-555-{environment[:4].upper()}-{i:02d}',
            'on_trial': settings['on_trial'],
            'trial_ends_at': timezone.now() + timedelta(days=settings['trial_days']),
            'domain': f"{company['domain_suffix']}.{settings['domain_base']}",
            'is_primary': True,
        }
        configs.append(config)
    
    return configs


def cleanup_demo_tenants(
    environment: str,
    verbosity: int = 1,
    dry_run: bool = True
) -> int:
    """
    Clean up demo tenants for a specific environment.
    
    Args:
        environment: Environment name
        verbosity: Output verbosity level
        dry_run: If True, only show what would be deleted without actually deleting
    
    Returns:
        Number of tenants that would be/were deleted
    
    Example:
        >>> # See what would be deleted
        >>> count = cleanup_demo_tenants('development', dry_run=True)
        >>> 
        >>> # Actually delete
        >>> count = cleanup_demo_tenants('development', dry_run=False)
    """
    # Find tenants matching environment prefix
    demo_tenants = Tenant.objects.filter(
        schema_name__startswith=f'{environment}_'
    )
    
    count = demo_tenants.count()
    
    if verbosity >= 1:
        if dry_run:
            print(f'\n🔍 DRY RUN: Would delete {count} demo tenants for {environment}:')
        else:
            print(f'\n🗑️  Deleting {count} demo tenants for {environment}:')
        
        for tenant in demo_tenants:
            print(f'  - {tenant.name} ({tenant.schema_name})')
    
    if not dry_run:
        demo_tenants.delete()
        if verbosity >= 1:
            print(f'\n✅ Deleted {count} demo tenants')
    else:
        if verbosity >= 1:
            print(f'\nTo actually delete, run with dry_run=False')
    
    return count
