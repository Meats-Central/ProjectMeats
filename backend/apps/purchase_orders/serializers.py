"""
Purchase Orders serializers for ProjectMeats.

Provides serialization for purchase order API endpoints.
"""
from rest_framework import serializers
from apps.purchase_orders.models import PurchaseOrder, CarrierPurchaseOrder, ColdStorageEntry


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "total_amount",
            "status",
            "order_date",
            "delivery_date",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on"]


class CarrierPurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for CarrierPurchaseOrder model."""

    class Meta:
        model = CarrierPurchaseOrder
        fields = [
            "id",
            "tenant",
            "date_time_stamp_created",
            "carrier",
            "supplier",
            "plant",
            "product",
            "pick_up_date",
            "delivery_date",
            "our_carrier_po_num",
            "carrier_name",
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
        read_only_fields = ["id", "date_time_stamp_created", "created_on", "modified_on"]


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

