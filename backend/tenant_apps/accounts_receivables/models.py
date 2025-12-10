"""
Accounts Receivables models for ProjectMeats.

Implements tenant ForeignKey field for shared-schema multi-tenancy.
"""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from apps.tenants.models import Tenant


class AccountsReceivable(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="accounts_receivables",
        help_text="Tenant this accounts receivable belongs to"
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="accounts_receivables",
    )
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Accounts Receivable"
        verbose_name_plural = "Accounts Receivables"
        indexes = [
            models.Index(fields=['tenant', 'invoice_number']),
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name} - ${self.amount}"
