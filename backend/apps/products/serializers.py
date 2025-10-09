"""
Serializers for Products app.
"""
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

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
            "unit_weight",
            "is_active",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on"]
