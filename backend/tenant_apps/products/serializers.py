"""
Serializers for Products app.
"""
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with tenant validation."""
    
    # Read-only fields for display
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "tenant",
            "product_code",
            "description_of_product_item",
            "type_of_protein",
            "fresh_or_frozen",
            "package_type",
            "net_or_catch",
            "edible_or_inedible",
            "tested_product",
            "supplier",
            "supplier_name",
            "supplier_item_number",
            "plants_available",
            "origin",
            "carton_type",
            "pcs_per_carton",
            "uom",
            "namp",
            "usda",
            "ub",
            "unit_weight",
            "is_active",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "tenant", "created_on", "modified_on"]
        extra_kwargs = {
            'product_code': {'required': True},
            'description_of_product_item': {'required': True},
        }
