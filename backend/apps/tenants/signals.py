"""
Signal handlers for tenant models.
Automatically sends invitation emails when TenantInvitation is created.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import TenantInvitation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TenantInvitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Automatically send email when a new invitation is created.
    
    Only sends email if:
    - Invitation was just created
    - Status is 'pending'
    - Email address is provided (not a reusable golden ticket)
    """
    if created and instance.status == 'pending' and instance.email:
        # Construct the invite link
        base_url = getattr(settings, 'FRONTEND_URL', 'https://meatscentral.com')
        invite_url = f"{base_url}/signup?token={instance.token}"
        
        subject = f"You've been invited to join {instance.tenant.name} on Project Meats"
        
        message = (
            f"Hello,\n\n"
            f"You have been invited to join the workspace '{instance.tenant.name}' as a {instance.role}.\n\n"
            f"Message from sender: {instance.message}\n\n"
            f"Click the link below to accept the invitation and set up your account:\n"
            f"{invite_url}\n\n"
            f"This link expires on {instance.expires_at.strftime('%Y-%m-%d')}.\n\n"
            f"Welcome aboard,\nThe Project Meats Team"
        )
        
        try:
            logger.info(f"📧 Sending invitation email to {instance.email} via SendGrid...")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            logger.info("✅ Email sent successfully.")
        except Exception as e:
            logger.exception(f"❌ Failed to send email: {str(e)}")

