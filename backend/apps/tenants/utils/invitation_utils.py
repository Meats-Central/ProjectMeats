"""
Invitation utilities for tenant onboarding.

This module provides functions for generating invitation links
and managing tenant invitations.
"""
from datetime import timedelta
from typing import Optional, Tuple

from django.http import HttpRequest
from django.utils import timezone

from apps.tenants.models import Tenant, TenantInvitation


def generate_invitation_link(
    tenant: Tenant,
    request: Optional[HttpRequest] = None,
    role: str = "user",
    days_valid: int = 7,
    email: Optional[str] = None,
    message: Optional[str] = None,
    invited_by=None,
) -> Tuple[TenantInvitation, str]:
    """
    Generate a reusable invitation link for a tenant.

    This function creates a new TenantInvitation and returns the corresponding
    signup URL that can be shared with potential users.

    Args:
        tenant: The Tenant instance to create an invitation for
        request: Optional HTTP request for domain detection
        role: Role to assign to new users (default: 'user')
            Choices: 'owner', 'admin', 'manager', 'user', 'readonly'
        days_valid: Number of days until invitation expires (default: 7)
        email: Optional specific email for the invitation
            If not provided, uses 'invite@{domain}'
        message: Optional custom message for the invitation
        invited_by: Optional User who created the invitation

    Returns:
        Tuple of (TenantInvitation, invitation_url)

    Raises:
        ValueError: If tenant has no domain configured

    Example:
        >>> from apps.tenants.models import Tenant
        >>> from apps.tenants.utils import generate_invitation_link
        >>>
        >>> tenant = Tenant.objects.get(slug='acme-corp')
        >>> invitation, url = generate_invitation_link(
        ...     tenant,
        ...     role='admin',
        ...     days_valid=14,
        ...     message='Welcome to the team!'
        ... )
        >>> print(f'Share this link: {url}')
    """
    # Get the domain for the invitation URL
    domain = _get_tenant_domain(tenant, request)

    # Generate email if not provided
    if not email:
        email = f"invite@{domain}"

    # Generate default message if not provided
    if not message:
        message = f"You have been invited to join {tenant.name}."

    # Validate role
    valid_roles = ["owner", "admin", "manager", "user", "readonly"]
    if role not in valid_roles:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {valid_roles}")

    # Create invitation
    invitation = TenantInvitation.objects.create(
        tenant=tenant,
        email=email,
        role=role,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=days_valid),
        message=message,
    )

    # Generate URL
    invitation_url = _build_invitation_url(domain, invitation.token)

    return invitation, invitation_url


def _get_tenant_domain(tenant: Tenant, request: Optional[HttpRequest] = None) -> str:
    """
    Get the appropriate domain for a tenant.

    Priority:
    1. Request host (if provided)
    2. Primary tenant domain
    3. Tenant's domain field
    4. Generated from slug

    Args:
        tenant: The Tenant instance
        request: Optional HTTP request

    Returns:
        Domain string

    Raises:
        ValueError: If no domain can be determined
    """
    # Use request host if available
    if request:
        return request.get_host()

    # Try to get primary domain from TenantDomain
    primary_domain = tenant.tenant_domains.filter(is_primary=True).first()
    if primary_domain:
        return primary_domain.domain

    # Try any domain
    any_domain = tenant.tenant_domains.first()
    if any_domain:
        return any_domain.domain

    # Fallback to tenant's domain field
    if tenant.domain:
        return tenant.domain

    # Generate from slug as last resort
    return f"{tenant.slug}.example.com"


def _build_invitation_url(domain: str, token: str) -> str:
    """
    Build the full invitation URL.

    Args:
        domain: The domain to use
        token: The invitation token

    Returns:
        Full invitation URL string
    """
    # Determine protocol based on domain
    if domain.startswith("localhost") or domain.startswith("127.0.0.1"):
        protocol = "http"
    else:
        protocol = "https"

    return f"{protocol}://{domain}/signup/?token={token}"


def get_invitation_by_token(token: str) -> Optional[TenantInvitation]:
    """
    Retrieve an invitation by its token.

    Args:
        token: The invitation token

    Returns:
        TenantInvitation if found and valid, None otherwise
    """
    try:
        invitation = TenantInvitation.objects.get(token=token)

        # Check and update expiration status
        invitation.check_and_update_expiration()

        return invitation
    except TenantInvitation.DoesNotExist:
        return None


def validate_invitation(token: str) -> dict:
    """
    Validate an invitation token and return details.

    Args:
        token: The invitation token

    Returns:
        dict with validation result and details:
        {
            'valid': bool,
            'invitation': TenantInvitation or None,
            'error': str or None,
            'tenant_name': str or None,
            'role': str or None,
        }
    """
    invitation = get_invitation_by_token(token)

    if not invitation:
        return {
            "valid": False,
            "invitation": None,
            "error": "Invitation not found",
            "tenant_name": None,
            "role": None,
        }

    if invitation.status != "pending":
        return {
            "valid": False,
            "invitation": invitation,
            "error": f"Invitation is {invitation.status}",
            "tenant_name": invitation.tenant.name,
            "role": invitation.role,
        }

    if invitation.is_expired:
        return {
            "valid": False,
            "invitation": invitation,
            "error": "Invitation has expired",
            "tenant_name": invitation.tenant.name,
            "role": invitation.role,
        }

    return {
        "valid": True,
        "invitation": invitation,
        "error": None,
        "tenant_name": invitation.tenant.name,
        "role": invitation.role,
    }
