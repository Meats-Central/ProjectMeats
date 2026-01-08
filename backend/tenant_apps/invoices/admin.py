"""
Django admin configuration for Invoices app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Invoice, Claim


@admin.register(Invoice)
class InvoiceAdmin(TenantFilteredAdmin):
    """Admin interface for Invoice model with tenant filtering."""

    list_display = (
        "invoice_number",
        "customer",
        "status",
        "total_amount",
        "due_date",
        "date_time_stamp",
    )
    list_filter = (
        "status",
        "date_time_stamp",
        "pick_up_date",
        "delivery_date",
        "due_date",
        "tested_product",
        "edible_or_inedible",
    )
    search_fields = (
        "invoice_number",
        "our_sales_order_num",
        "delivery_po_num",
        "customer__name",
    )
    readonly_fields = ("date_time_stamp", "created_on", "modified_on")
    raw_id_fields = ("customer", "sales_order", "product")

    fieldsets = (
        (
            "Invoice Information",
            {
                "fields": (
                    "invoice_number",
                    "date_time_stamp",
                    "status",
                    "due_date",
                )
            },
        ),
        (
            "Related Entities",
            {
                "fields": (
                    "customer",
                    "sales_order",
                    "product",
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
            "Order References",
            {
                "fields": (
                    "our_sales_order_num",
                    "delivery_po_num",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "accounting_payable_contact_name",
                    "accounting_payable_contact_phone",
                    "accounting_payable_contact_email",
                )
            },
        ),
        (
            "Product Details",
            {
                "fields": (
                    "type_of_protein",
                    "description_of_product_item",
                    "quantity",
                    "total_weight",
                    "weight_unit",
                    "edible_or_inedible",
                    "tested_product",
                )
            },
        ),
        (
            "Financial Details",
            {
                "fields": (
                    "unit_price",
                    "total_amount",
                    "tax_amount",
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



@admin.register(Claim)
class ClaimAdmin(TenantFilteredAdmin):
    """Admin interface for Claim model with tenant filtering."""
    
    list_display = (
        "claim_number",
        "claim_type",
        "status",
        "claimed_amount",
        "claim_date",
        "assigned_to",
    )
    list_filter = (
        "claim_type",
        "status",
        "claim_date",
        "resolution_date",
    )
    search_fields = (
        "claim_number",
        "reason",
        "description",
        "resolution_notes",
    )
    readonly_fields = ("created_on", "modified_on")
    raw_id_fields = ("supplier", "customer", "purchase_order", "sales_order", "invoice", "assigned_to", "created_by")
