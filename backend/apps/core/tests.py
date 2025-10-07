"""
Unit tests for core models.

Tests cover base models and common functionality used across all apps:
- Protein model
- StatusChoices enum
- StatusModel abstract model
- TimestampModel abstract model
- OwnedModel abstract model
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .models import (
    Protein,
    StatusChoices,
    StatusModel,
    TimestampModel,
    OwnedModel,
)


class ProteinModelTests(TestCase):
    """Test cases for Protein model."""

    def test_protein_creation(self):
        """Test basic protein creation."""
        protein = Protein.objects.create(name="Beef")
        
        self.assertEqual(protein.name, "Beef")
        self.assertIsNotNone(protein.id)

    def test_protein_unique_name(self):
        """Test that protein names must be unique."""
        Protein.objects.create(name="Pork")
        
        with self.assertRaises(Exception):
            Protein.objects.create(name="Pork")

    def test_protein_str_method(self):
        """Test string representation of protein."""
        protein = Protein.objects.create(name="Chicken")
        
        self.assertEqual(str(protein), "Chicken")

    def test_protein_ordering(self):
        """Test that proteins are ordered by name."""
        Protein.objects.create(name="Lamb")
        Protein.objects.create(name="Beef")
        Protein.objects.create(name="Pork")
        
        proteins = Protein.objects.all()
        
        self.assertEqual(proteins[0].name, "Beef")
        self.assertEqual(proteins[1].name, "Lamb")
        self.assertEqual(proteins[2].name, "Pork")

    def test_protein_max_length(self):
        """Test protein name max length constraint."""
        long_name = "A" * 50
        protein = Protein.objects.create(name=long_name)
        
        self.assertEqual(len(protein.name), 50)

    def test_protein_verbose_names(self):
        """Test verbose name configuration."""
        self.assertEqual(Protein._meta.verbose_name, "Protein")
        self.assertEqual(Protein._meta.verbose_name_plural, "Proteins")


class StatusChoicesTests(TestCase):
    """Test cases for StatusChoices enum."""

    def test_status_choices_values(self):
        """Test that all status choices are defined correctly."""
        self.assertEqual(StatusChoices.ACTIVE, "active")
        self.assertEqual(StatusChoices.INACTIVE, "inactive")
        self.assertEqual(StatusChoices.ARCHIVED, "archived")

    def test_status_choices_labels(self):
        """Test that status choice labels are correct."""
        self.assertEqual(StatusChoices.ACTIVE.label, "Active")
        self.assertEqual(StatusChoices.INACTIVE.label, "Inactive")
        self.assertEqual(StatusChoices.ARCHIVED.label, "Archived")

    def test_status_choices_count(self):
        """Test that we have exactly 3 status choices."""
        self.assertEqual(len(StatusChoices.choices), 3)


class StatusModelTests(TestCase):
    """Test cases for StatusModel abstract model."""

    def test_status_model_is_abstract(self):
        """Test that StatusModel is an abstract model."""
        self.assertTrue(StatusModel._meta.abstract)

    def test_status_model_has_status_field(self):
        """Test that StatusModel defines status field."""
        status_field = StatusModel._meta.get_field('status')
        
        self.assertEqual(status_field.max_length, 20)
        self.assertEqual(status_field.choices, StatusChoices.choices)
        self.assertEqual(status_field.default, StatusChoices.ACTIVE)


class TimestampModelTests(TestCase):
    """Test cases for TimestampModel abstract model."""

    def test_timestamp_model_is_abstract(self):
        """Test that TimestampModel is an abstract model."""
        self.assertTrue(TimestampModel._meta.abstract)

    def test_timestamp_model_has_timestamp_fields(self):
        """Test that TimestampModel defines created_on and modified_on fields."""
        created_field = TimestampModel._meta.get_field('created_on')
        modified_field = TimestampModel._meta.get_field('modified_on')
        
        self.assertTrue(created_field.auto_now_add)
        self.assertTrue(modified_field.auto_now)

    def test_timestamp_model_with_protein(self):
        """Test timestamp functionality using a model that could inherit it."""
        # Protein doesn't inherit TimestampModel, but we test the concept
        # by verifying the fields are properly defined
        created_field = TimestampModel._meta.get_field('created_on')
        modified_field = TimestampModel._meta.get_field('modified_on')
        
        self.assertIsNotNone(created_field)
        self.assertIsNotNone(modified_field)


class OwnedModelTests(TestCase):
    """Test cases for OwnedModel abstract model."""

    def setUp(self):
        """Set up test users."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )

    def test_owned_model_is_abstract(self):
        """Test that OwnedModel is an abstract model."""
        self.assertTrue(OwnedModel._meta.abstract)

    def test_owned_model_inherits_timestamp_model(self):
        """Test that OwnedModel inherits from TimestampModel."""
        # Check that OwnedModel has timestamp fields
        created_field = OwnedModel._meta.get_field('created_on')
        modified_field = OwnedModel._meta.get_field('modified_on')
        
        self.assertIsNotNone(created_field)
        self.assertIsNotNone(modified_field)

    def test_owned_model_has_ownership_fields(self):
        """Test that OwnedModel defines ownership fields."""
        owner_field = OwnedModel._meta.get_field('owner')
        created_by_field = OwnedModel._meta.get_field('created_by')
        modified_by_field = OwnedModel._meta.get_field('modified_by')
        
        # Check field types
        from django.db.models import ForeignKey
        self.assertIsInstance(owner_field, ForeignKey)
        self.assertIsInstance(created_by_field, ForeignKey)
        self.assertIsInstance(modified_by_field, ForeignKey)
        
        # Check cascade behavior
        from django.db.models import CASCADE
        self.assertEqual(owner_field.remote_field.on_delete, CASCADE)
        self.assertEqual(created_by_field.remote_field.on_delete, CASCADE)
        self.assertEqual(modified_by_field.remote_field.on_delete, CASCADE)

    def test_owned_model_related_names(self):
        """Test that related names use %(class)s pattern."""
        created_by_field = OwnedModel._meta.get_field('created_by')
        modified_by_field = OwnedModel._meta.get_field('modified_by')
        
        # The related_name should contain the pattern for substitution
        self.assertEqual(created_by_field.remote_field.related_name, "%(class)s_created")
        self.assertEqual(modified_by_field.remote_field.related_name, "%(class)s_modified")

    def test_owned_model_help_text(self):
        """Test that help text is set for ownership fields."""
        owner_field = OwnedModel._meta.get_field('owner')
        created_by_field = OwnedModel._meta.get_field('created_by')
        modified_by_field = OwnedModel._meta.get_field('modified_by')
        
        self.assertEqual(owner_field.help_text, "User who owns this entity")
        self.assertEqual(created_by_field.help_text, "User who created this entity")
        self.assertEqual(modified_by_field.help_text, "User who last modified this entity")
