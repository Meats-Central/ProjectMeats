"""
Email utilities for sending tenant invitation emails.
"""
import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_invitation_email(invitation):
    """
    Send an invitation email to the invitee.

    Args:
        invitation: TenantInvitation instance

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get inviter name if available
        inviter_name = None
        if invitation.invited_by:
            inviter_name = (
                invitation.invited_by.get_full_name() or invitation.invited_by.username
            )

        # Build signup URL with token
        # Use FRONTEND_URL from settings if available, otherwise use a default
        frontend_url = getattr(settings, "FRONTEND_URL", "https://app.meatscentral.com")
        signup_url = f"{frontend_url}/signup?token={invitation.token}"

        # Prepare context for templates
        context = {
            "tenant_name": invitation.tenant.name,
            "email": invitation.email,
            "role": invitation.role,
            "inviter_name": inviter_name,
            "signup_url": signup_url,
            "expires_at": invitation.expires_at,
            "message": invitation.message,
            "current_year": datetime.now().year,
        }

        # Render HTML and plain text versions
        html_message = render_to_string("tenants/email/invitation_email.html", context)
        plain_message = render_to_string("tenants/email/invitation_email.txt", context)

        # Email subject
        subject = f"You're invited to join {invitation.tenant.name} on ProjectMeats"

        # Sender email - use DEFAULT_FROM_EMAIL from settings
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@meatscentral.com")

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[invitation.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(
            f"Invitation email sent successfully to {invitation.email} "
            f"for tenant {invitation.tenant.name} (invitation ID: {invitation.id})"
        )
        return True

    except Exception as e:
        logger.error(
            f"Failed to send invitation email to {invitation.email} "
            f"for tenant {invitation.tenant.name} (invitation ID: {invitation.id}): {str(e)}",
            exc_info=True,
        )
        return False
