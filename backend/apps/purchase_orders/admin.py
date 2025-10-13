"""
Django admin configuration for Purchase Orders app.
"""
from django.contrib import admin
from .models import PurchaseOrder, CarrierPurchaseOrder, ColdStorageEntry


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


@admin.register(CarrierPurchaseOrder)
class CarrierPurchaseOrderAdmin(admin.ModelAdmin):
    """Admin interface for CarrierPurchaseOrder model."""

    list_display = (
        "our_carrier_po_num",
        "carrier",
        "supplier",
        "pick_up_date",
        "date_time_stamp_created",
    )
    list_filter = (
        "date_time_stamp_created",
        "pick_up_date",
        "delivery_date",
        "payment_terms",
        "type_of_protein",
        "fresh_or_frozen",
        "weight_unit",
    )
    search_fields = (
        "our_carrier_po_num",
        "carrier_name",
        "carrier__name",
        "supplier__name",
    )
    readonly_fields = ("date_time_stamp_created", "created_on", "modified_on")
    raw_id_fields = ("carrier", "supplier", "plant", "product")

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "our_carrier_po_num",
                    "carrier_name",
                    "carrier",
                    "supplier",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "date_time_stamp_created",
                    "pick_up_date",
                    "delivery_date",
                )
            },
        ),
        (
            "Payment & Credit",
            {
                "fields": (
                    "payment_terms",
                    "credit_limits",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Product Details",
            {
                "fields": (
                    "product",
                    "type_of_protein",
                    "fresh_or_frozen",
                    "package_type",
                    "net_or_catch",
                    "edible_or_inedible",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Weight & Quantity",
            {
                "fields": (
                    "total_weight",
                    "weight_unit",
                    "quantity",
                ),
            },
        ),
        (
            "Carrier Details",
            {
                "fields": (
                    "how_carrier_make_appointment",
                    "departments_of_carrier",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Relationships",
            {"fields": ("plant",), "classes": ("collapse",)},
        ),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )


@admin.register(ColdStorageEntry)
class ColdStorageEntryAdmin(admin.ModelAdmin):
    """Admin interface for ColdStorageEntry model."""

    list_display = (
        "id",
        "status_of_load",
        "item_production_date",
        "supplier_po",
        "customer_sales_order",
        "total_cost",
        "date_time_stamp_created",
    )
    list_filter = (
        "status_of_load",
        "item_production_date",
        "date_time_stamp_created",
    )
    search_fields = (
        "item_description",
        "supplier_po__order_number",
        "customer_sales_order__our_sales_order_num",
    )
    readonly_fields = ("date_time_stamp_created", "created_on", "modified_on")
    raw_id_fields = ("supplier_po", "customer_sales_order", "product")

    fieldsets = (
        (
            "Entry Information",
            {
                "fields": (
                    "date_time_stamp_created",
                    "status_of_load",
                    "item_production_date",
                )
            },
        ),
        (
            "Related Orders",
            {
                "fields": (
                    "supplier_po",
                    "customer_sales_order",
                    "product",
                )
            },
        ),
        (
            "Product Details",
            {
                "fields": ("item_description",),
            },
        ),
        (
            "Boxing Details",
            {
                "fields": (
                    "finished_weight",
                    "shrink",
                    "boxing_cost",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Cold Storage Costs",
            {
                "fields": (
                    "cold_storage_cost",
                    "total_cost",
                ),
            },
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )
