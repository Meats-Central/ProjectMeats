"""
Tests for Products app models.
"""
from decimal import Decimal
from django.test import TestCase
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.core.models import (
    CartonTypeChoices,
    EdibleInedibleChoices,
    FreshOrFrozenChoices,
    OriginChoices,
    PackageTypeChoices,
    ProteinTypeChoices,
)


class ProductModelTest(TestCase):
    """Test cases for Product model."""

    def setUp(self):
        """Set up test data."""
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@test.com",
        )

    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            product_code="TEST001",
            description_of_product_item="Test Beef Product",
            type_of_protein=ProteinTypeChoices.BEEF,
            fresh_or_frozen=FreshOrFrozenChoices.FROZEN,
            package_type=PackageTypeChoices.BOXED_WAX_LINED,
            tested_product=True,
            is_active=True,
        )
        
        self.assertEqual(product.product_code, "TEST001")
        self.assertEqual(product.type_of_protein, "Beef")
        self.assertTrue(product.tested_product)
        self.assertTrue(product.is_active)

    def test_product_str_representation(self):
        """Test the string representation of a product."""
        product = Product.objects.create(
            product_code="TEST002",
            description_of_product_item="Test Chicken Product",
        )
        
        self.assertIn("TEST002", str(product))
        self.assertIn("Test Chicken Product", str(product))

    def test_product_with_supplier(self):
        """Test creating a product with supplier relationship."""
        product = Product.objects.create(
            product_code="TEST003",
            description_of_product_item="Test Product with Supplier",
            supplier=self.supplier,
            supplier_item_number="SUP123",
            plants_available="TX, WI, MI",
            origin=OriginChoices.DOMESTIC,
        )
        
        self.assertEqual(product.supplier, self.supplier)
        self.assertEqual(product.supplier_item_number, "SUP123")
        self.assertEqual(product.plants_available, "TX, WI, MI")
        self.assertEqual(product.origin, "Domestic")

    def test_product_packaging_details(self):
        """Test product with packaging details from Excel schema."""
        product = Product.objects.create(
            product_code="TEST004",
            description_of_product_item="BF Trim 50's - TESTED",
            type_of_protein=ProteinTypeChoices.BEEF,
            fresh_or_frozen=FreshOrFrozenChoices.FRESH,
            carton_type=CartonTypeChoices.WAXED_LINED,
            pcs_per_carton="4/10",
            uom="LB",
            edible_or_inedible=EdibleInedibleChoices.EDIBLE,
            tested_product=True,
        )
        
        self.assertEqual(product.carton_type, "Waxed Lined")
        self.assertEqual(product.pcs_per_carton, "4/10")
        self.assertEqual(product.uom, "LB")
        self.assertTrue(product.tested_product)

    def test_product_codes(self):
        """Test product with NAMP, USDA, and UB codes."""
        product = Product.objects.create(
            product_code="TEST005",
            description_of_product_item="Test Product with Codes",
            namp="82265",
            usda="USDA123",
            ub="UB456",
        )
        
        self.assertEqual(product.namp, "82265")
        self.assertEqual(product.usda, "USDA123")
        self.assertEqual(product.ub, "UB456")

    def test_product_unit_weight(self):
        """Test product with unit weight."""
        product = Product.objects.create(
            product_code="TEST006",
            description_of_product_item="Test Product with Weight",
            unit_weight=Decimal("50.25"),
        )
        
        self.assertEqual(product.unit_weight, Decimal("50.25"))


