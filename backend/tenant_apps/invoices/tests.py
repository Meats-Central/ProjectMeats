"""
Tests for Invoices app models.
"""
import uuid
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
        unique_id = uuid.uuid4().hex[:8]
        self.customer = Customer.objects.create(
            name=f"Test Customer {unique_id}",
            email=f"customer-{unique_id}@test.com",
        )

    def test_create_invoice(self):
        """Test creating an invoice."""
        unique_id = uuid.uuid4().hex[:8]
        invoice = Invoice.objects.create(
            invoice_number=f"INV-{unique_id}",
            customer=self.customer,
            total_amount=Decimal("1500.00"),
            status=InvoiceStatus.DRAFT,
        )
        
        self.assertEqual(invoice.invoice_number, f"INV-{unique_id}")
        self.assertEqual(invoice.customer, self.customer)
        self.assertEqual(invoice.total_amount, Decimal("1500.00"))
        self.assertEqual(invoice.status, "draft")

    def test_invoice_str_representation(self):
        """Test the string representation of an invoice."""
        unique_id = uuid.uuid4().hex[:8]
        invoice = Invoice.objects.create(
            invoice_number=f"INV-{unique_id}",
            customer=self.customer,
            total_amount=Decimal("2000.00"),
        )
        
        self.assertEqual(str(invoice), f"INV-INV-{unique_id}")

