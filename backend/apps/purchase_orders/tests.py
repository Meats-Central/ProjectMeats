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


"""
Tests for Purchase Orders API endpoints and version history.

Validates purchase order creation, updates, and version history tracking.
"""
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.purchase_orders.models import PurchaseOrder, PurchaseOrderHistory
from apps.suppliers.models import Supplier
from apps.tenants.models import Tenant, TenantUser
from decimal import Decimal
from datetime import date


class PurchaseOrderHistoryTests(APITestCase):
    """Test cases for Purchase Order version history."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        # Associate user with tenant
        TenantUser.objects.create(tenant=self.tenant, user=self.user, role="owner")

        # Create a supplier for testing
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="123-456-7890",
            tenant=self.tenant,
        )

    def test_history_created_on_new_po(self):
        """Test that history entry is created when a new PO is created."""
        # Create a purchase order
        po = PurchaseOrder.objects.create(
            order_number="PO-001",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        # Check that a history entry was created
        self.assertEqual(PurchaseOrderHistory.objects.count(), 1)
        history = PurchaseOrderHistory.objects.first()
        self.assertEqual(history.purchase_order, po)
        self.assertEqual(history.change_type, "created")
        self.assertIsNotNone(history.changed_data)

    def test_history_created_on_update(self):
        """Test that history entry is created when a PO is updated."""
        # Create a purchase order
        po = PurchaseOrder.objects.create(
            order_number="PO-002",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        # Clear initial history
        initial_count = PurchaseOrderHistory.objects.count()

        # Update the purchase order
        po.total_amount = Decimal("1500.00")
        po.save(update_fields=["total_amount"])

        # Check that a new history entry was created
        self.assertEqual(PurchaseOrderHistory.objects.count(), initial_count + 1)
        history = PurchaseOrderHistory.objects.order_by("-created_on").first()
        self.assertEqual(history.change_type, "updated")

    def test_history_api_endpoint(self):
        """Test the history API endpoint returns correct data."""
        # Create a purchase order
        po = PurchaseOrder.objects.create(
            order_number="PO-003",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        # Update it a couple of times
        po.total_amount = Decimal("1500.00")
        po.save()

        po.status = "approved"
        po.save()

        # Call the history endpoint using the DRF router URL pattern
        url = f"/api/v1/purchase-orders/{po.pk}/history/"
        response = self.client.get(url, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Should have at least 3 entries (created + 2 updates)
        self.assertGreaterEqual(len(response.data), 3)

    def test_history_tracks_user(self):
        """Test that history entries can track user who made changes."""
        # Create a purchase order with user context
        PurchaseOrder.objects.create(
            order_number="PO-004",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        # Note: In real scenario, signal would need user passed
        # For now, we verify the structure exists
        history = PurchaseOrderHistory.objects.first()
        self.assertIsNotNone(history)
        # User tracking available but may be None if not passed
        self.assertIn(
            "changed_by", [f.name for f in PurchaseOrderHistory._meta.get_fields()]
        )

    def test_history_entries_ordered_by_date(self):
        """Test that history entries are returned in reverse chronological order."""
        # Create and update a purchase order multiple times
        po = PurchaseOrder.objects.create(
            order_number="PO-005",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        po.total_amount = Decimal("1200.00")
        po.save()

        po.total_amount = Decimal("1300.00")
        po.save()

        # Get history entries
        history_entries = PurchaseOrderHistory.objects.filter(purchase_order=po)

        # Verify they're in descending order by created_on
        timestamps = [h.created_on for h in history_entries]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_multiple_pos_separate_history(self):
        """Test that different POs have separate history entries."""
        # Create two purchase orders
        po1 = PurchaseOrder.objects.create(
            order_number="PO-006",
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        po2 = PurchaseOrder.objects.create(
            order_number="PO-007",
            supplier=self.supplier,
            total_amount=Decimal("2000.00"),
            order_date=date.today(),
            tenant=self.tenant,
        )

        # Check that each has its own history
        po1_history_count = PurchaseOrderHistory.objects.filter(
            purchase_order=po1
        ).count()
        po2_history_count = PurchaseOrderHistory.objects.filter(
            purchase_order=po2
        ).count()

        self.assertEqual(po1_history_count, 1)
        self.assertEqual(po2_history_count, 1)

        # Update po1
        po1.total_amount = Decimal("1500.00")
        po1.save()

        # Check that only po1's history increased
        self.assertEqual(
            PurchaseOrderHistory.objects.filter(purchase_order=po1).count(),
            po1_history_count + 1,
        )
        self.assertEqual(
            PurchaseOrderHistory.objects.filter(purchase_order=po2).count(),
            po2_history_count,
        )
