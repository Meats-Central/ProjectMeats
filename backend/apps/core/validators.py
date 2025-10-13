"""
Validators for ProjectMeats.

Provides OWASP-compliant validators for common field types.
"""
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
import re


# Email validator following OWASP recommendations
email_validator = EmailValidator(
    message="Enter a valid email address.",
    code="invalid_email",
)


# Phone validator following OWASP recommendations
# Allows formats: +1-234-567-8900, (123) 456-7890, 123-456-7890, 1234567890, +11234567890
phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]+$',
    message="Enter a valid phone number. Formats: +1-234-567-8900, (123) 456-7890, 123-456-7890, 1234567890",
    code="invalid_phone",
)


def validate_phone_number(value):
    """
    Validate phone number format and length.
    
    Ensures phone has at least 10 digits after removing formatting.
    """
    if not value:
        return
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    if len(digits_only) < 10 or len(digits_only) > 15:
        raise ValidationError(
            "Phone number must contain between 10 and 15 digits."
        )


# ZIP code validator (US and Canadian postal codes)
zip_code_validator = RegexValidator(
    regex=r'^[0-9]{5}(-[0-9]{4})?$|^[A-Za-z][0-9][A-Za-z]\s?[0-9][A-Za-z][0-9]$',
    message="Enter a valid US ZIP code (12345 or 12345-6789) or Canadian postal code (A1A 1A1)",
    code="invalid_zip_code",
)


def validate_product_code(value):
    """
    Validate product code format.
    
    Product codes should be alphanumeric and may contain hyphens or underscores.
    Length: 3-50 characters.
    """
    if not value:
        raise ValidationError("Product code cannot be empty.")
    
    if len(value) < 3 or len(value) > 50:
        raise ValidationError("Product code must be between 3 and 50 characters.")
    
    if not re.match(r'^[A-Za-z0-9\-_]+$', value):
        raise ValidationError(
            "Product code can only contain letters, numbers, hyphens, and underscores."
        )


def validate_positive_decimal(value):
    """
    Validate that a decimal field is positive.
    """
    if value is not None and value < 0:
        raise ValidationError("Value must be positive.")


def validate_non_negative_decimal(value):
    """
    Validate that a decimal field is non-negative (0 or positive).
    """
    if value is not None and value < 0:
        raise ValidationError("Value cannot be negative.")


def validate_percentage(value):
    """
    Validate that a value is between 0 and 100 (percentage).
    """
    if value is not None:
        if value < 0 or value > 100:
            raise ValidationError("Percentage must be between 0 and 100.")
