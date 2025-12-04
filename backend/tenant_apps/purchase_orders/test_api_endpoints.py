"""
Basic API endpoint tests for purchase orders.
Tests the 404 fix for purchase-orders endpoint.
"""
import pytest
from django.test import Client
from rest_framework import status


@pytest.mark.django_db
class TestPurchaseOrdersAPI:
    """Test suite for purchase orders API endpoints."""

    def test_purchase_orders_list_endpoint_exists(self):
        """Test that the purchase orders list endpoint is accessible."""
        client = Client()
        response = client.get("/api/v1/purchase-orders/")

        # Should return 200 OK, not 404
        assert response.status_code == status.HTTP_200_OK

        # Should return JSON data structure
        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_purchase_orders_without_trailing_slash_redirects(self):
        """Test that URLs without trailing slash redirect properly."""
        client = Client()
        response = client.get("/api/v1/purchase-orders", follow=False)

        # Should return 301 redirect due to APPEND_SLASH=True
        assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY

    def test_purchase_orders_with_trailing_slash_redirect_works(self):
        """Test that the redirect to trailing slash version works."""
        client = Client()
        response = client.get("/api/v1/purchase-orders", follow=True)

        # Should eventually return 200 after redirect
        assert response.status_code == status.HTTP_200_OK
