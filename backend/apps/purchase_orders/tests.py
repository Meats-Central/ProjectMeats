"""
Tests for Purchase Orders app models.
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.purchase_orders.models import (
    PurchaseOrder,
    CarrierPurchaseOrder,
    ColdStorageEntry,
    PurchaseOrderStatus,
)
from apps.suppliers.models import Supplier
from apps.carriers.models import Carrier
from apps.customers.models import Customer
from apps.products.models import Product
from apps.plants.models import Plant
from apps.sales_orders.models import SalesOrder
from apps.core.models import (
    AccountingPaymentTermsChoices,
    EdibleInedibleChoices,
    FreshOrFrozenChoices,
    ProteinTypeChoices,
    WeightUnitChoices,
)


class CarrierPurchaseOrderModelTest(TestCase):
    """Test cases for CarrierPurchaseOrder model."""

    def setUp(self):
        """Set up test data."""
        self.carrier = Carrier.objects.create(
            name="Test Carrier",
            email="carrier@test.com",
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@test.com",
        )
        self.plant = Plant.objects.create(
            name="Test Plant",
            city="Test City",
        )
        self.product = Product.objects.create(
            product_code="TEST001",
            description_of_product_item="Test Product",
        )

    def test_create_carrier_purchase_order(self):
        """Test creating a carrier purchase order."""
        carrier_po = CarrierPurchaseOrder.objects.create(
            carrier=self.carrier,
            supplier=self.supplier,
            our_carrier_po_num="CPO-001",
            carrier_name="Test Carrier",
            pick_up_date=timezone.now().date(),
        )
        
        self.assertEqual(carrier_po.carrier, self.carrier)
        self.assertEqual(carrier_po.supplier, self.supplier)
        self.assertEqual(carrier_po.our_carrier_po_num, "CPO-001")
        self.assertIsNotNone(carrier_po.date_time_stamp_created)

    def test_carrier_purchase_order_with_product_details(self):
        """Test carrier PO with product details from Excel schema."""
        carrier_po = CarrierPurchaseOrder.objects.create(
            carrier=self.carrier,
            supplier=self.supplier,
            plant=self.plant,
            product=self.product,
            our_carrier_po_num="CPO-002",
            type_of_protein=ProteinTypeChoices.BEEF,
            fresh_or_frozen=FreshOrFrozenChoices.FRESH,
            edible_or_inedible=EdibleInedibleChoices.EDIBLE,
            total_weight=Decimal("1000.50"),
            weight_unit=WeightUnitChoices.LBS,
            quantity=100,
        )
        
        self.assertEqual(carrier_po.type_of_protein, "Beef")
        self.assertEqual(carrier_po.fresh_or_frozen, "Fresh")
        self.assertEqual(carrier_po.total_weight, Decimal("1000.50"))
        self.assertEqual(carrier_po.weight_unit, "LBS")
        self.assertEqual(carrier_po.quantity, 100)

    def test_carrier_purchase_order_with_payment_terms(self):
        """Test carrier PO with payment and credit terms."""
        carrier_po = CarrierPurchaseOrder.objects.create(
            carrier=self.carrier,
            supplier=self.supplier,
            payment_terms=AccountingPaymentTermsChoices.WIRE,
            our_carrier_po_num="CPO-003",
        )
        
        self.assertEqual(carrier_po.payment_terms, "Wire")

    def test_carrier_purchase_order_str_representation(self):
        """Test the string representation of carrier PO."""
        carrier_po = CarrierPurchaseOrder.objects.create(
            carrier=self.carrier,
            supplier=self.supplier,
            our_carrier_po_num="CPO-004",
        )
        
        self.assertIn("CPO-004", str(carrier_po))


class ColdStorageEntryModelTest(TestCase):
    """Test cases for ColdStorageEntry model."""

    def setUp(self):
        """Set up test data."""
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@test.com",
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@test.com",
        )
        self.supplier_po = PurchaseOrder.objects.create(
            order_number="PO-001",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=timezone.now().date(),
        )
        self.product = Product.objects.create(
            product_code="TEST001",
            description_of_product_item="Test Product",
        )

    def test_create_cold_storage_entry(self):
        """Test creating a cold storage entry."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            status_of_load="Matched",
            item_description="50% Beef Trim fresh - Tested",
            item_production_date=timezone.now().date(),
        )
        
        self.assertEqual(entry.supplier_po, self.supplier_po)
        self.assertEqual(entry.status_of_load, "Matched")
        self.assertEqual(entry.item_description, "50% Beef Trim fresh - Tested")
        self.assertIsNotNone(entry.date_time_stamp_created)

    def test_cold_storage_entry_with_boxing_details(self):
        """Test cold storage entry with boxing details."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            status_of_load="Matched",
            finished_weight=Decimal("950.00"),
            shrink=Decimal("50.00"),
            boxing_cost=Decimal("100.00"),
        )
        
        self.assertEqual(entry.finished_weight, Decimal("950.00"))
        self.assertEqual(entry.shrink, Decimal("50.00"))
        self.assertEqual(entry.boxing_cost, Decimal("100.00"))

    def test_cold_storage_entry_with_costs(self):
        """Test cold storage entry with cost calculations."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            status_of_load="Matched",
            boxing_cost=Decimal("100.00"),
            cold_storage_cost=Decimal("50.00"),
            total_cost=Decimal("150.00"),
        )
        
        self.assertEqual(entry.boxing_cost, Decimal("100.00"))
        self.assertEqual(entry.cold_storage_cost, Decimal("50.00"))
        self.assertEqual(entry.total_cost, Decimal("150.00"))

    def test_cold_storage_entry_tbd_status(self):
        """Test cold storage entry with TBD status."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            status_of_load="TBD - Not Matched",
            item_description="Unmatched product",
        )
        
        self.assertEqual(entry.status_of_load, "TBD - Not Matched")

    def test_cold_storage_entry_str_representation(self):
        """Test the string representation of cold storage entry."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            status_of_load="Matched",
        )
        
        self.assertIn("Cold Storage Entry", str(entry))
        self.assertIn("Matched", str(entry))

    def test_cold_storage_entry_with_product(self):
        """Test cold storage entry with product relationship."""
        entry = ColdStorageEntry.objects.create(
            supplier_po=self.supplier_po,
            product=self.product,
            status_of_load="Matched",
            item_description="Test product in storage",
        )
        
        self.assertEqual(entry.product, self.product)
