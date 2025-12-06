"""
Tests for Invoices app models.
"""
from unittest import skip
from django.test import TestCase
from decimal import Decimal
from tenant_apps.invoices.models import Invoice, InvoiceStatus
from tenant_apps.customers.models import Customer


@skip("Requires tenant-scoped objects - needs schema-based test setup")
class InvoiceModelTest(TestCase):
    """Test cases for Invoice model."""

    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@test.com",
        )

    def test_create_invoice(self):
        """Test creating an invoice."""
        invoice = Invoice.objects.create(
            invoice_number="INV001",
            customer=self.customer,
            total_amount=Decimal("1500.00"),
            status=InvoiceStatus.DRAFT,
        )
        
        self.assertEqual(invoice.invoice_number, "INV001")
        self.assertEqual(invoice.customer, self.customer)
        self.assertEqual(invoice.total_amount, Decimal("1500.00"))
        self.assertEqual(invoice.status, "draft")

    def test_invoice_str_representation(self):
        """Test the string representation of an invoice."""
        invoice = Invoice.objects.create(
            invoice_number="INV002",
            customer=self.customer,
            total_amount=Decimal("2000.00"),
        )
        
        self.assertEqual(str(invoice), "INV-INV002")

