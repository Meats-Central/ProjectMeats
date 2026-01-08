"""
Purchase Orders serializers for ProjectMeats.

Provides serialization for purchase order API endpoints.
"""
from rest_framework import serializers
from tenant_apps.purchase_orders.models import PurchaseOrder, CarrierPurchaseOrder, ColdStorageEntry
from tenant_apps.purchase_orders.models import PurchaseOrderHistory
from tenant_apps.locations.serializers import LocationListSerializer


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""
    
    # Nested location serializers (read-only)
    pick_up_location_details = LocationListSerializer(source='pick_up_location', read_only=True)
    delivery_location_details = LocationListSerializer(source='delivery_location', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "product",
            "total_amount",
            "status",
            "order_date",
            "delivery_date",
            "pick_up_date",
            "logistics_scenario",
            "pick_up_location",
            "pick_up_location_details",
            "delivery_location",
            "delivery_location_details",
            "plant",
            "carrier",
            "carrier_release_format",
            "payment_terms",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "pick_up_location_details", "delivery_location_details"]


class CarrierPurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for CarrierPurchaseOrder model."""
    
    # Nested location serializers (read-only)
    pick_up_location_details = LocationListSerializer(source='pick_up_location', read_only=True)
    delivery_location_details = LocationListSerializer(source='delivery_location', read_only=True)

    class Meta:
        model = CarrierPurchaseOrder
        fields = [
            "id",
            "tenant",
            "date_time_stamp_created",
            "carrier",
            "supplier",
            "plant",
            "pick_up_location",
            "pick_up_location_details",
            "delivery_location",
            "delivery_location_details",
            "product",
            "linked_order",
            "sales_order",
            "pick_up_date",
            "delivery_date",
            "our_carrier_po_num",
            "carrier_name",
            "carrier_release_format",
            "payment_terms",
            "credit_limits",
            "type_of_protein",
            "fresh_or_frozen",
            "package_type",
            "net_or_catch",
            "edible_or_inedible",
            "total_weight",
            "weight_unit",
            "quantity",
            "how_carrier_make_appointment",
            "departments_of_carrier",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "date_time_stamp_created", "created_on", "modified_on", "pick_up_location_details", "delivery_location_details"]


class ColdStorageEntrySerializer(serializers.ModelSerializer):
    """Serializer for ColdStorageEntry model."""

    class Meta:
        model = ColdStorageEntry
        fields = [
            "id",
            "tenant",
            "date_time_stamp_created",
            "supplier_po",
            "customer_sales_order",
            "product",
            "status_of_load",
            "item_production_date",
            "item_description",
            "finished_weight",
            "shrink",
            "boxing_cost",
            "cold_storage_cost",
            "total_cost",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "date_time_stamp_created", "created_on", "modified_on"]

class PurchaseOrderHistorySerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderHistory model."""

    changed_by_username = serializers.CharField(
        source="changed_by.username", read_only=True, allow_null=True
    )
    purchase_order_number = serializers.CharField(
        source="purchase_order.order_number", read_only=True
    )

    class Meta:
        model = PurchaseOrderHistory
        fields = [
            "id",
            "purchase_order",
            "purchase_order_number",
            "changed_data",
            "changed_by",
            "changed_by_username",
            "change_type",
            "created_on",
            "modified_on",
        ]
        read_only_fields = [
            "id",
            "purchase_order",
            "changed_data",
            "changed_by",
            "change_type",
            "created_on",
            "modified_on",
        ]
