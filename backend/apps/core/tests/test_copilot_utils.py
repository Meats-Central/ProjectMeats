"""
Tests for Copilot-added utility functions.

This test file verifies the Copilot workflow and automation system.
"""
from apps.core.validators import format_display_name
from django.test import TestCase


class FormatDisplayNameTest(TestCase):
    """Test cases for format_display_name utility function."""

    def test_format_with_both_names(self):
        """Test formatting with both first and last names provided."""
        result = format_display_name("John", "Doe")
        self.assertEqual(result, "John Doe")

    def test_format_with_first_name_only(self):
        """Test formatting with only first name provided."""
        result = format_display_name("John", "")
        self.assertEqual(result, "John")

    def test_format_with_last_name_only(self):
        """Test formatting with only last name provided."""
        result = format_display_name("", "Doe")
        self.assertEqual(result, "Doe")

    def test_format_with_no_names(self):
        """Test formatting with no names provided."""
        result = format_display_name("", "")
        self.assertEqual(result, "Unknown User")

    def test_format_with_whitespace(self):
        """Test formatting handles whitespace correctly."""
        result = format_display_name("  John  ", "  Doe  ")
        self.assertEqual(result, "John Doe")

    def test_format_with_none_values(self):
        """Test formatting handles None values correctly."""
        result = format_display_name(None, None)
        self.assertEqual(result, "Unknown User")

    def test_format_with_mixed_none_and_empty(self):
        """Test formatting with mixed None and empty strings."""
        result = format_display_name(None, "Doe")
        self.assertEqual(result, "Doe")

        result = format_display_name("John", None)
        self.assertEqual(result, "John")
