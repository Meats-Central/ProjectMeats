"""
Django admin configuration for Accounts Receivables app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import AccountsReceivable


@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(TenantFilteredAdmin):
    """Admin interface for AccountsReceivable model with tenant filtering."""

    list_display = (
        "invoice_number",
        "customer",
        "amount",
        "due_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "due_date", "created_at")
    search_fields = ("invoice_number", "customer__name", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Invoice Information",
            {"fields": ("invoice_number", "customer", "amount", "due_date", "status")},
        ),
        ("Details", {"fields": ("description",)}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields
        return ("created_at", "updated_at")
