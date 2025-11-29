"""
Django admin configuration for Sales Orders app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import SalesOrder


@admin.register(SalesOrder)
class SalesOrderAdmin(TenantFilteredAdmin):
    """Admin interface for SalesOrder model with tenant filtering."""

    list_display = (
        "our_sales_order_num",
        "customer",
        "supplier",
        "status",
        "pick_up_date",
        "delivery_date",
        "total_amount",
        "date_time_stamp",
    )
    list_filter = (
        "status",
        "pick_up_date",
        "delivery_date",
        "date_time_stamp",
        "weight_unit",
    )
    search_fields = (
        "our_sales_order_num",
        "delivery_po_num",
        "carrier_release_num",
        "customer__name",
        "supplier__name",
    )
    readonly_fields = ("date_time_stamp", "created_on", "modified_on")
    raw_id_fields = ("supplier", "customer", "carrier", "product", "plant", "contact")

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "our_sales_order_num",
                    "date_time_stamp",
                    "status",
                )
            },
        ),
        (
            "Related Entities",
            {
                "fields": (
                    "supplier",
                    "customer",
                    "carrier",
                    "product",
                    "plant",
                    "contact",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "pick_up_date",
                    "delivery_date",
                )
            },
        ),
        (
            "Order Details",
            {
                "fields": (
                    "delivery_po_num",
                    "carrier_release_num",
                    "quantity",
                    "total_weight",
                    "weight_unit",
                    "total_amount",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("tenant", "created_on", "modified_on"),
                "classes": ("collapse",),
            },
        ),
    )

