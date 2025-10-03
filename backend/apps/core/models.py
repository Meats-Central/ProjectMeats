"""
Core models for ProjectMeats.

Provides base models and common functionality used across all apps.
"""
from django.contrib.auth.models import User
from django.db import models


class Protein(models.Model):
    """Protein model for meat types used across suppliers and customers."""

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Protein type (e.g., Beef, Pork, Chicken, Lamb)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Protein"
        verbose_name_plural = "Proteins"

    def __str__(self):
        return self.name

        
        


class StatusChoices(models.TextChoices):
    """Common status choices for entities."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"


class StatusModel(models.Model):
    """Abstract base model for entities with status."""

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the entity",
    )

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    """Abstract base model for entities with timestamps."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OwnedModel(TimestampModel):
    """Abstract base model for entities with ownership."""

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who owns this entity",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_created",
        help_text="User who created this entity",
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_modified",
        help_text="User who last modified this entity",
    )

    class Meta:
        abstract = True
