"""
Tests for Products app models.
"""
from django.test import TestCase
from apps.products.models import Product
from apps.core.models import (
    ProteinTypeChoices,
    FreshOrFrozenChoices,
    PackageTypeChoices,
)


class ProductModelTest(TestCase):
    """Test cases for Product model."""

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

