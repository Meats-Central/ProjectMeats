"""
Management command to seed products for tenants.

Usage:
    python manage.py seed_products --all                    # Seed all active tenants
    python manage.py seed_products --tenant_name "Acme Inc" # Seed specific tenant
"""
from django.core.management.base import BaseCommand, CommandError
from apps.tenants.models import Tenant
from tenant_apps.products.models import Product


class Command(BaseCommand):
    help = "Seed products for tenant(s). Use --all for all active tenants or --tenant_name for specific tenant."

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Seed all active tenants',
        )
        parser.add_argument(
            '--tenant_name',
            type=str,
            help='Tenant name to seed (exact match)',
        )

    def handle(self, *args, **options):
        # Hardcoded product data (32 products)
        products_data = [
            {'protein': 'Beef', 'description': 'Trim 50\'s - Tested', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Not Tested', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 85\'s - Tested', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 85\'s - Not Tested', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Positive', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Cooker ONLY', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s', 'edible_or_inedible': 'Inedible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Chicken', 'description': 'BSB - Boneless Skinless Breast', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly-Multiple', 'pcs_per_carton': '4/10', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Chicken', 'description': 'BSB - Boneless Skinless Breast', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Tested', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Tested', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Cooker ONLY', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Cooker ONLY', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Cooker ONLY', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Beef', 'description': 'Trim 50\'s - Cooker ONLY', 'edible_or_inedible': 'Edible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Edible', 'type': 'Fresh', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Inedible', 'type': 'Fresh', 'type_of_packaging': 'Combo', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Packer'},
            {'protein': 'Chicken', 'description': 'Trim Skin', 'edible_or_inedible': 'Inedible', 'type': 'Frozen', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly Bulk', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Catch', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Beef', 'description': 'Trim 85\'s', 'edible_or_inedible': 'Inedible', 'type': 'Frozen', 'type_of_packaging': 'Nude', 'carton_type': 'Nude', 'pcs_per_carton': '1/1', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Beef', 'description': None, 'edible_or_inedible': None, 'type': 'Fresh', 'type_of_packaging': 'Boxed', 'carton_type': 'Poly-Multiple', 'pcs_per_carton': '4/10', 'uom': 'LB', 'weight': 'Net', 'origin': 'Packer'},
            {'protein': 'Pork', 'description': None, 'edible_or_inedible': None, 'type': 'Frozen', 'type_of_packaging': 'Combo', 'carton_type': 'Waxed Lined', 'pcs_per_carton': '6/10', 'uom': 'KG', 'weight': 'Catch', 'origin': 'Boxed Cold Storage'},
            {'protein': 'Chicken', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': 'Nude', 'carton_type': 'Nude', 'pcs_per_carton': '8/10', 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Fowl', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': 'COV', 'pcs_per_carton': '1/1', 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Turkey', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': 'CVP', 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Lamb', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': 'Poly Bulk', 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Veal', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': None, 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Seafood', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': None, 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Venson', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': None, 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
            {'protein': 'Mics', 'description': None, 'edible_or_inedible': None, 'type': None, 'type_of_packaging': None, 'carton_type': None, 'pcs_per_carton': None, 'uom': None, 'weight': None, 'origin': None},
        ]

        # Determine which tenants to seed
        if options['all']:
            tenants = Tenant.objects.filter(is_active=True)
            if not tenants.exists():
                raise CommandError("No active tenants found.")
            self.stdout.write(self.style.SUCCESS(f"Seeding {tenants.count()} active tenant(s)..."))
        elif options['tenant_name']:
            try:
                tenants = [Tenant.objects.get(name=options['tenant_name'])]
            except Tenant.DoesNotExist:
                raise CommandError(f"Tenant '{options['tenant_name']}' not found.")
        else:
            raise CommandError("Must specify --all or --tenant_name")

        # Seed products for each tenant
        total_created = 0
        total_skipped = 0

        for tenant in tenants:
            self.stdout.write(f"\n🌱 Seeding tenant: {tenant.name} (slug: {tenant.slug})")
            created_count = 0
            skipped_count = 0

            for index, row in enumerate(products_data, start=1):
                # Generate unique product code per tenant
                product_code = f"{tenant.slug.upper()}-PROD-{index:03d}"
                
                # Map fields to Product model
                description = row['description'] or row['protein']
                
                # Map choices to model field names
                protein_map = {
                    'Beef': 'Beef',
                    'Chicken': 'Chicken',
                    'Pork': 'Pork',
                    'Lamb': 'Lamb',
                    'Turkey': 'Turkey',
                    'Fowl': 'Chicken',  # Map Fowl to Chicken
                    'Veal': 'Other',  # Map Veal to Other
                    'Seafood': 'Fish',  # Map Seafood to Fish
                    'Venson': 'Other',  # Map Venson to Other (typo of Venison)
                    'Mics': 'Other',  # Map Mics to Other
                }
                
                edible_map = {
                    'Edible': 'Edible',
                    'Inedible': 'Inedible',
                }
                
                fresh_frozen_map = {
                    'Fresh': 'Fresh',
                    'Frozen': 'Frozen',
                }
                
                package_map = {
                    'Combo': 'Combo bins',
                    'Boxed': 'Boxed wax lined',
                    'Nude': 'Nude',
                }
                
                carton_map = {
                    'Poly Bulk': 'Poly-Multiple',
                    'Poly-Multiple': 'Poly-Multiple',
                    'Waxed Lined': 'Waxed Lined',
                    'Nude': 'Cardboard',  # Default for Nude
                    'COV': 'Cardboard',
                    'CVP': 'Cardboard',
                }
                
                weight_map = {
                    'Catch': 'Catch',
                    'Net': 'Net',
                }
                
                origin_map = {
                    'Packer': 'Domestic',
                    'Boxed Cold Storage': 'Domestic',
                }
                
                # Build defaults dict
                defaults = {
                    'description_of_product_item': description,
                    'type_of_protein': protein_map.get(row['protein'], ''),
                    'edible_or_inedible': edible_map.get(row['edible_or_inedible'], ''),
                    'fresh_or_frozen': fresh_frozen_map.get(row['type'], ''),
                    'package_type': package_map.get(row['type_of_packaging'], ''),
                    'carton_type': carton_map.get(row['carton_type'], ''),
                    'pcs_per_carton': row['pcs_per_carton'] or '',
                    'uom': row['uom'] or '',
                    'net_or_catch': weight_map.get(row['weight'], ''),
                    'origin': origin_map.get(row['origin'], ''),
                    'is_active': True,
                }
                
                # Create or get product
                product, created = Product.objects.get_or_create(
                    tenant=tenant,
                    product_code=product_code,
                    defaults=defaults
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"  ✓ Created: {product_code} - {description[:50]}")
                else:
                    skipped_count += 1
                    self.stdout.write(f"  ⊙ Exists:  {product_code} - {description[:50]}")
            
            total_created += created_count
            total_skipped += skipped_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Tenant '{tenant.name}': {created_count} created, {skipped_count} skipped"
                )
            )

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Summary: {total_created} products created, {total_skipped} already existed across {len(tenants)} tenant(s)"
            )
        )
