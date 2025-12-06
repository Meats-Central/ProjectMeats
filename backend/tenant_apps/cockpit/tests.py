"""
Tests for Cockpit aggregated search functionality.

Verifies multi-tenant search across Customer, Supplier, and PurchaseOrder models.
"""
import uuid
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
        # Create test tenant with unique identifiers
        unique_id = uuid.uuid4().hex[:8]
        cls.unique_id = unique_id
        cls.tenant = Tenant.objects.create(
            name=f'Test Cockpit Tenant {unique_id}',
            slug=f'test-cockpit-{unique_id}',
            contact_email=f'test-{unique_id}@example.com',
            is_active=True,
        )
    
    def setUp(self):
        self.client = APIClient()
        
        # Generate unique identifier for this test run
        unique_id = uuid.uuid4().hex[:8]
        
        # Create test user with unique identifiers
        self.user = User.objects.create_user(
            username=f'testuser-{unique_id}',
            password='testpass123',
            email=f'test-{unique_id}@example.com'
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
        
        # Create test data with unique identifiers
        self.customer = Customer.objects.create(
            name=f'Acme Corporation {unique_id}',
            contact_person=f'John Doe {unique_id}',
            email=f'john-{unique_id}@acme.com',
            phone='555-1234'
        )
        
        self.supplier = Supplier.objects.create(
            name=f'Global Supplies {unique_id}',
            contact_person=f'Jane Smith {unique_id}',
            email=f'jane-{unique_id}@global.com',
            phone='555-5678'
        )
        
        self.purchase_order = PurchaseOrder.objects.create(
            order_number=f'PO-2024-{unique_id}',
            our_purchase_order_num=f'INT-{unique_id}',
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
        self.assertIn('Acme Corporation', customers[0]['name'])
        self.assertIn('John Doe', customers[0]['contact_name'])
    
    def test_search_by_order_number(self):
        """Test searching for orders by order number."""
        response = self.client.get('/api/v1/cockpit/slots/', {'q': 'PO-2024'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        orders = [item for item in response.data if item['type'] == 'order']
        self.assertEqual(len(orders), 1)
        self.assertIn('PO-2024', orders[0]['order_number'])
        self.assertIn('Global Supplies', orders[0]['supplier_name'])
    
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
