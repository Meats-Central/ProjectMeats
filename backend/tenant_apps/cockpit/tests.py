"""
Tests for Cockpit aggregated search functionality.

Verifies multi-tenant search across Customer, Supplier, and PurchaseOrder models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.tenants.models import Tenant, TenantUser
from tenant_apps.customers.models import Customer
from tenant_apps.suppliers.models import Supplier
from tenant_apps.purchase_orders.models import PurchaseOrder


class CockpitSearchTestCase(TestCase):
    """Test cockpit search API with multi-tenancy."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test tenant
        cls.tenant = Tenant.objects.create(
            name='Test Cockpit Tenant',
            slug='test-cockpit',
            contact_email='test@example.com',
            is_active=True,
        )
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Associate user with tenant
        TenantUser.objects.create(
            user=self.user,
            tenant=self.tenant,
            role='admin',
            is_active=True
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.customer = Customer.objects.create(
            name='Acme Corporation',
            contact_person='John Doe',
            email='john@acme.com',
            phone='555-1234'
        )
        
        self.supplier = Supplier.objects.create(
            name='Global Supplies',
            contact_person='Jane Smith',
            email='jane@global.com',
            phone='555-5678'
        )
        
        self.purchase_order = PurchaseOrder.objects.create(
            order_number='PO-2024-001',
            our_purchase_order_num='INT-001',
            supplier=self.supplier,
            status='pending',
            order_date='2024-01-01',
            total_amount='1500.00'
        )
    
    def test_search_returns_all_types(self):
        """Test that search returns results from all model types."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'o'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should find results containing 'o'
        types = [item['type'] for item in response.data]
        self.assertIn('customer', types)  # Acme Corporatio[n]
        self.assertIn('supplier', types)  # Global Supplies
        self.assertIn('order', types)  # PO-2024-001
    
    def test_search_by_customer_name(self):
        """Test searching for customers by name."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'Acme'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        customers = [item for item in response.data if item['type'] == 'customer']
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0]['name'], 'Acme Corporation')
        self.assertEqual(customers[0]['contact_name'], 'John Doe')
    
    def test_search_by_order_number(self):
        """Test searching for orders by order number."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'PO-2024'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        orders = [item for item in response.data if item['type'] == 'order']
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['order_number'], 'PO-2024-001')
        self.assertEqual(orders[0]['supplier_name'], 'Global Supplies')
    
    def test_empty_search_returns_empty(self):
        """Test that empty query returns empty results."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': ''})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_no_results_for_nonexistent_query(self):
        """Test that search with no matches returns empty."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'ZZZZZZZZZ'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_requires_authentication(self):
        """Test that endpoint requires authentication."""
        self.client.logout()
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'test'})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
