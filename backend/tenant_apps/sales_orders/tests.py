"""
Tests for Sales Orders app models.
"""
import uuid
from unittest import skip, TestCase
from tenant_apps.sales_orders.models import SalesOrder, SalesOrderStatus
from tenant_apps.suppliers.models import Supplier
from tenant_apps.customers.models import Customer
from apps.core.models import WeightUnitChoices


@skip("Requires tenant-scoped objects - needs schema-based test setup")
class SalesOrderModelTest(TestCase):
    """Test cases for SalesOrder model."""

    def setUp(self):
        """Set up test data."""
        unique_id = uuid.uuid4().hex[:8]
        self.supplier = Supplier.objects.create(
            name=f"Test Supplier {unique_id}",
            email=f"supplier-{unique_id}@test.com",
        )
        self.customer = Customer.objects.create(
            name=f"Test Customer {unique_id}",
            email=f"customer-{unique_id}@test.com",
        )

    def test_create_sales_order(self):
        """Test creating a sales order."""
        unique_id = uuid.uuid4().hex[:8]
        sales_order = SalesOrder.objects.create(
            our_sales_order_num=f"SO-{unique_id}",
            supplier=self.supplier,
            customer=self.customer,
            status=SalesOrderStatus.PENDING,
            quantity=100,
            total_weight=1000.50,
            weight_unit=WeightUnitChoices.LBS,
        )
        
        self.assertEqual(sales_order.our_sales_order_num, f"SO-{unique_id}")
        self.assertEqual(sales_order.supplier, self.supplier)
        self.assertEqual(sales_order.customer, self.customer)
        self.assertEqual(sales_order.status, "pending")

    def test_sales_order_str_representation(self):
        """Test the string representation of a sales order."""
        unique_id = uuid.uuid4().hex[:8]
        sales_order = SalesOrder.objects.create(
            our_sales_order_num=f"SO-{unique_id}",
            supplier=self.supplier,
            customer=self.customer,
        )
        
        self.assertEqual(str(sales_order), f"SO-SO-{unique_id}")

