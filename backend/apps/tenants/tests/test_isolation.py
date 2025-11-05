"""
Tests for multi-tenancy data isolation.

This module tests that data is properly isolated between tenants
and that users can only access data belonging to their tenant.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser
from apps.suppliers.models import Supplier
from apps.customers.models import Customer
from apps.purchase_orders.models import PurchaseOrder
from apps.plants.models import Plant
from apps.contacts.models import Contact
from apps.carriers.models import Carrier
from apps.accounts_receivables.models import AccountsReceivable
from decimal import Decimal
from datetime import date


class TenantIsolationTests(TestCase):
    """Test cases for tenant data isolation."""

    def setUp(self):
        """Set up test data with two tenants and users."""
        # Create two tenants
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            slug="tenant-1",
            contact_email="admin@tenant1.com",
        )
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            slug="tenant-2",
            contact_email="admin@tenant2.com",
        )

        # Create users for each tenant
        self.user1 = User.objects.create_user(
            username="user1", email="user1@tenant1.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@tenant2.com", password="testpass123"
        )

        # Associate users with their tenants
        TenantUser.objects.create(tenant=self.tenant1, user=self.user1, role="owner")
        TenantUser.objects.create(tenant=self.tenant2, user=self.user2, role="owner")

    def test_supplier_isolation(self):
        """Test that suppliers are isolated between tenants."""
        # Create suppliers for each tenant
        supplier1 = Supplier.objects.create(
            tenant=self.tenant1,
            name="Supplier 1",
            email="supplier1@test.com",
        )
        supplier2 = Supplier.objects.create(
            tenant=self.tenant2,
            name="Supplier 2",
            email="supplier2@test.com",
        )

        # Verify tenant1 can only see its supplier
        tenant1_suppliers = Supplier.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_suppliers.count(), 1)
        self.assertEqual(tenant1_suppliers.first().id, supplier1.id)

        # Verify tenant2 can only see its supplier
        tenant2_suppliers = Supplier.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_suppliers.count(), 1)
        self.assertEqual(tenant2_suppliers.first().id, supplier2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(supplier2, tenant1_suppliers)
        self.assertNotIn(supplier1, tenant2_suppliers)

    def test_customer_isolation(self):
        """Test that customers are isolated between tenants."""
        # Create customers for each tenant
        customer1 = Customer.objects.create(
            tenant=self.tenant1,
            name="Customer 1",
            email="customer1@test.com",
        )
        customer2 = Customer.objects.create(
            tenant=self.tenant2,
            name="Customer 2",
            email="customer2@test.com",
        )

        # Verify tenant1 can only see its customer
        tenant1_customers = Customer.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_customers.count(), 1)
        self.assertEqual(tenant1_customers.first().id, customer1.id)

        # Verify tenant2 can only see its customer
        tenant2_customers = Customer.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_customers.count(), 1)
        self.assertEqual(tenant2_customers.first().id, customer2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(customer2, tenant1_customers)
        self.assertNotIn(customer1, tenant2_customers)

    def test_purchase_order_isolation(self):
        """Test that purchase orders are isolated between tenants."""
        # Create suppliers for each tenant
        supplier1 = Supplier.objects.create(
            tenant=self.tenant1,
            name="Supplier 1",
            email="supplier1@test.com",
        )
        supplier2 = Supplier.objects.create(
            tenant=self.tenant2,
            name="Supplier 2",
            email="supplier2@test.com",
        )

        # Create purchase orders for each tenant
        po1 = PurchaseOrder.objects.create(
            tenant=self.tenant1,
            order_number="PO-001",
            supplier=supplier1,
            total_amount=Decimal("1000.00"),
            order_date=date.today(),
        )
        po2 = PurchaseOrder.objects.create(
            tenant=self.tenant2,
            order_number="PO-002",
            supplier=supplier2,
            total_amount=Decimal("2000.00"),
            order_date=date.today(),
        )

        # Verify tenant1 can only see its purchase order
        tenant1_pos = PurchaseOrder.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_pos.count(), 1)
        self.assertEqual(tenant1_pos.first().id, po1.id)

        # Verify tenant2 can only see its purchase order
        tenant2_pos = PurchaseOrder.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_pos.count(), 1)
        self.assertEqual(tenant2_pos.first().id, po2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(po2, tenant1_pos)
        self.assertNotIn(po1, tenant2_pos)

    def test_plant_isolation(self):
        """Test that plants are isolated between tenants."""
        # Create plants for each tenant
        plant1 = Plant.objects.create(
            tenant=self.tenant1,
            name="Plant 1",
            code="P1",
            address="123 Main St",
            city="City 1",
            state="State 1",
            zip_code="12345",
        )
        plant2 = Plant.objects.create(
            tenant=self.tenant2,
            name="Plant 2",
            code="P2",
            address="456 Oak Ave",
            city="City 2",
            state="State 2",
            zip_code="67890",
        )

        # Verify tenant1 can only see its plant
        tenant1_plants = Plant.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_plants.count(), 1)
        self.assertEqual(tenant1_plants.first().id, plant1.id)

        # Verify tenant2 can only see its plant
        tenant2_plants = Plant.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_plants.count(), 1)
        self.assertEqual(tenant2_plants.first().id, plant2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(plant2, tenant1_plants)
        self.assertNotIn(plant1, tenant2_plants)

    def test_contact_isolation(self):
        """Test that contacts are isolated between tenants."""
        # Create contacts for each tenant
        contact1 = Contact.objects.create(
            tenant=self.tenant1,
            first_name="John",
            last_name="Doe",
            email="john@tenant1.com",
        )
        contact2 = Contact.objects.create(
            tenant=self.tenant2,
            first_name="Jane",
            last_name="Smith",
            email="jane@tenant2.com",
        )

        # Verify tenant1 can only see its contact
        tenant1_contacts = Contact.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_contacts.count(), 1)
        self.assertEqual(tenant1_contacts.first().id, contact1.id)

        # Verify tenant2 can only see its contact
        tenant2_contacts = Contact.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_contacts.count(), 1)
        self.assertEqual(tenant2_contacts.first().id, contact2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(contact2, tenant1_contacts)
        self.assertNotIn(contact1, tenant2_contacts)

    def test_carrier_isolation(self):
        """Test that carriers are isolated between tenants."""
        # Create carriers for each tenant
        carrier1 = Carrier.objects.create(
            tenant=self.tenant1,
            name="Carrier 1",
            code="C1",
        )
        carrier2 = Carrier.objects.create(
            tenant=self.tenant2,
            name="Carrier 2",
            code="C2",
        )

        # Verify tenant1 can only see its carrier
        tenant1_carriers = Carrier.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_carriers.count(), 1)
        self.assertEqual(tenant1_carriers.first().id, carrier1.id)

        # Verify tenant2 can only see its carrier
        tenant2_carriers = Carrier.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_carriers.count(), 1)
        self.assertEqual(tenant2_carriers.first().id, carrier2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(carrier2, tenant1_carriers)
        self.assertNotIn(carrier1, tenant2_carriers)

    def test_accounts_receivable_isolation(self):
        """Test that accounts receivable are isolated between tenants."""
        # Create customers for each tenant
        customer1 = Customer.objects.create(
            tenant=self.tenant1,
            name="Customer 1",
            email="customer1@test.com",
        )
        customer2 = Customer.objects.create(
            tenant=self.tenant2,
            name="Customer 2",
            email="customer2@test.com",
        )

        # Create accounts receivable for each tenant
        ar1 = AccountsReceivable.objects.create(
            tenant=self.tenant1,
            customer=customer1,
            invoice_number="INV-001",
            amount=Decimal("500.00"),
            due_date=date.today(),
        )
        ar2 = AccountsReceivable.objects.create(
            tenant=self.tenant2,
            customer=customer2,
            invoice_number="INV-002",
            amount=Decimal("750.00"),
            due_date=date.today(),
        )

        # Verify tenant1 can only see its accounts receivable
        tenant1_ars = AccountsReceivable.objects.for_tenant(self.tenant1)
        self.assertEqual(tenant1_ars.count(), 1)
        self.assertEqual(tenant1_ars.first().id, ar1.id)

        # Verify tenant2 can only see its accounts receivable
        tenant2_ars = AccountsReceivable.objects.for_tenant(self.tenant2)
        self.assertEqual(tenant2_ars.count(), 1)
        self.assertEqual(tenant2_ars.first().id, ar2.id)

        # Verify no cross-tenant visibility
        self.assertNotIn(ar2, tenant1_ars)
        self.assertNotIn(ar1, tenant2_ars)

    def test_null_tenant_not_visible(self):
        """Test that entities without tenant are not visible."""
        # Create entities without tenant (legacy data)
        Supplier.objects.create(
            name="Legacy Supplier",
            email="legacy@test.com",
        )
        Customer.objects.create(
            name="Legacy Customer",
            email="legacy@test.com",
        )

        # Verify neither tenant can see legacy data
        self.assertEqual(Supplier.objects.for_tenant(self.tenant1).count(), 0)
        self.assertEqual(Supplier.objects.for_tenant(self.tenant2).count(), 0)
        self.assertEqual(Customer.objects.for_tenant(self.tenant1).count(), 0)
        self.assertEqual(Customer.objects.for_tenant(self.tenant2).count(), 0)
