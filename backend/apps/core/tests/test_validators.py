"""
Tests for Core app validators.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.core.validators import (
    email_validator,
    phone_validator,
    zip_code_validator,
    validate_product_code,
    validate_positive_decimal,
    validate_non_negative_decimal,
    validate_percentage,
)


class EmailValidatorTest(TestCase):
    """Test cases for email validator."""

    def test_valid_emails(self):
        """Test that valid emails pass validation."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "test123@test-domain.com",
        ]
        
        for email in valid_emails:
            try:
                email_validator(email)
            except ValidationError:
                self.fail(f"Valid email '{email}' failed validation")

    def test_invalid_emails(self):
        """Test that invalid emails fail validation."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test @example.com",
            "",
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                email_validator(email)


class PhoneValidatorTest(TestCase):
    """Test cases for phone validator."""

    def test_valid_phone_numbers(self):
        """Test that valid phone numbers pass validation."""
        valid_phones = [
            "+1-234-567-8900",
            "(123) 456-7890",
            "123-456-7890",
            "1234567890",
            "+11234567890",
        ]
        
        for phone in valid_phones:
            try:
                phone_validator(phone)
            except ValidationError:
                self.fail(f"Valid phone '{phone}' failed validation")

    def test_invalid_phone_numbers(self):
        """Test that invalid phone numbers fail validation."""
        invalid_phones = [
            "abc",  # Letters
            "!@#$%",  # Special chars
            "",  # Empty
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                phone_validator(phone)


class ZipCodeValidatorTest(TestCase):
    """Test cases for ZIP code validator."""

    def test_valid_zip_codes(self):
        """Test that valid ZIP codes pass validation."""
        valid_zips = [
            "12345",
            "12345-6789",
            "A1A 1A1",  # Canadian
            "A1A1A1",   # Canadian without space
        ]
        
        for zip_code in valid_zips:
            try:
                zip_code_validator(zip_code)
            except ValidationError:
                self.fail(f"Valid ZIP '{zip_code}' failed validation")

    def test_invalid_zip_codes(self):
        """Test that invalid ZIP codes fail validation."""
        invalid_zips = [
            "1234",      # Too short
            "123456",    # Too long for US
            "ABCDEF",
            "",
        ]
        
        for zip_code in invalid_zips:
            with self.assertRaises(ValidationError):
                zip_code_validator(zip_code)


class ProductCodeValidatorTest(TestCase):
    """Test cases for product code validator."""

    def test_valid_product_codes(self):
        """Test that valid product codes pass validation."""
        valid_codes = [
            "ABC123",
            "TEST-001",
            "PRODUCT_CODE_1",
            "123",
        ]
        
        for code in valid_codes:
            try:
                validate_product_code(code)
            except ValidationError:
                self.fail(f"Valid product code '{code}' failed validation")

    def test_invalid_product_codes(self):
        """Test that invalid product codes fail validation."""
        invalid_codes = [
            "",  # Empty
            "AB",  # Too short
            "A" * 51,  # Too long
            "TEST CODE",  # Contains space
            "TEST@CODE",  # Contains invalid character
        ]
        
        for code in invalid_codes:
            with self.assertRaises(ValidationError):
                validate_product_code(code)


class DecimalValidatorTest(TestCase):
    """Test cases for decimal validators."""

    def test_validate_positive_decimal(self):
        """Test positive decimal validator."""
        # Valid positive values
        validate_positive_decimal(Decimal("10.50"))
        validate_positive_decimal(Decimal("0.01"))
        validate_positive_decimal(None)  # None is allowed
        
        # Invalid negative value
        with self.assertRaises(ValidationError):
            validate_positive_decimal(Decimal("-1.00"))
        
        with self.assertRaises(ValidationError):
            validate_positive_decimal(Decimal("-0.01"))

    def test_validate_non_negative_decimal(self):
        """Test non-negative decimal validator."""
        # Valid non-negative values
        validate_non_negative_decimal(Decimal("10.50"))
        validate_non_negative_decimal(Decimal("0.00"))
        validate_non_negative_decimal(None)  # None is allowed
        
        # Invalid negative value
        with self.assertRaises(ValidationError):
            validate_non_negative_decimal(Decimal("-1.00"))

    def test_validate_percentage(self):
        """Test percentage validator."""
        # Valid percentages
        validate_percentage(Decimal("0"))
        validate_percentage(Decimal("50.5"))
        validate_percentage(Decimal("100"))
        validate_percentage(None)  # None is allowed
        
        # Invalid percentages
        with self.assertRaises(ValidationError):
            validate_percentage(Decimal("-1"))
        
        with self.assertRaises(ValidationError):
            validate_percentage(Decimal("101"))
