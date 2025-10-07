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
        "delivery_date",
        "created_on",
    )
    list_filter = ("status", "order_date", "delivery_date", "created_on")
    search_fields = ("order_number", "supplier__name", "notes")
    readonly_fields = ("created_on", "modified_on")

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_number", "supplier", "total_amount", "status")},
        ),
        ("Dates", {"fields": ("order_date", "delivery_date")}),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
