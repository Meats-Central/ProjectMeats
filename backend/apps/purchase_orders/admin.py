"""
Django admin configuration for Purchase Orders app.
"""
from django.contrib import admin
from .models import PurchaseOrder


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin interface for PurchaseOrder model."""

    list_display = (
        "order_number",
        "supplier",
        "total_amount",
        "status",
        "order_date",
        "pick_up_date",
        "delivery_date",
        "created_on",
    )
    list_filter = (
        "status",
        "order_date",
        "pick_up_date",
        "delivery_date",
        "weight_unit",
        "created_on",
    )
    search_fields = (
        "order_number",
        "our_purchase_order_num",
        "supplier_confirmation_order_num",
        "carrier_release_num",
        "supplier__name",
        "notes",
    )
    readonly_fields = ("date_time_stamp", "created_on", "modified_on")
    raw_id_fields = ("supplier", "carrier", "plant", "contact")

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "our_purchase_order_num",
                    "supplier_confirmation_order_num",
                    "supplier",
                    "total_amount",
                    "status",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "date_time_stamp",
                    "order_date",
                    "pick_up_date",
                    "delivery_date",
                )
            },
        ),
        (
            "Carrier & Logistics",
            {
                "fields": (
                    "carrier",
                    "carrier_release_format",
                    "carrier_release_num",
                    "how_carrier_make_appointment",
                )
            },
        ),
        (
            "Order Details",
            {
                "fields": (
                    "quantity",
                    "total_weight",
                    "weight_unit",
                )
            },
        ),
        (
            "Relationships",
            {"fields": ("plant", "contact")},
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )
