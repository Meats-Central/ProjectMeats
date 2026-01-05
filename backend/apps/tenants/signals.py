"""
Signal handlers for tenant models.
Automatically sends invitation emails when TenantInvitation is created.
Ensures owners have Django admin access.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import TenantInvitation, TenantUser

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TenantInvitation, dispatch_uid="send_invitation_email_once")
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Automatically send email when a new invitation is created.
    
    Only sends email if:
    - Invitation was just created
    - Status is 'pending'
    - Email address is provided (not a reusable golden ticket)
    
    Note: dispatch_uid prevents duplicate signal connections during Django reload.
    """
    if created and instance.status == 'pending' and instance.email:
        # Log configuration status
        logger.info("=" * 60)
        logger.info("📧 Preparing to send invitation email")
        logger.info(f"Recipient: {instance.email}")
        logger.info(f"Tenant: {instance.tenant.name}")
        logger.info(f"Role: {instance.role}")
        logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"SENDGRID_API_KEY: {'✅ SET' if getattr(settings, 'SENDGRID_API_KEY', '') else '❌ NOT SET'}")
        logger.info("=" * 60)
        
        # Construct the invite link
        base_url = getattr(settings, 'FRONTEND_URL', 'https://meatscentral.com')
        invite_url = f"{base_url}/signup?token={instance.token}"
        
        subject = f"You've been invited to join {instance.tenant.name} on Meats Central"
        
        message = (
            f"Hello,\n\n"
            f"You have been invited to join '{instance.tenant.name}' as a {instance.role}.\n\n"
            f"{instance.message}\n\n"
            f"Click the link below to accept the invitation and set up your account:\n"
            f"{invite_url}\n\n"
            f"This link expires on {instance.expires_at.strftime('%Y-%m-%d')}.\n\n"
            f"Welcome to easy meat management,\n"
            f"The Meats Central Team"
        )
        
        try:
            logger.info(f"📤 Sending invitation email to {instance.email} via SendGrid Web API...")
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            logger.info(f"✅ Email sent successfully! (result={result})")
        except Exception as e:
            logger.exception(f"❌ Failed to send email to {instance.email}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            # Re-raise to ensure error is visible
            raise


@receiver(post_save, sender=TenantUser, dispatch_uid="ensure_owner_has_staff_access")
def ensure_owner_has_staff_access(sender, instance, created, **kwargs):
    """
    Automatically grant Django admin access to users with 'owner' role.
    
    When a TenantUser is created or updated with role='owner', this signal
    ensures the associated User has is_staff=True so they can access the
    Django admin interface.
    
    Note: dispatch_uid prevents duplicate signal connections during Django reload.
    """
    if instance.role == 'owner' and not instance.user.is_staff:
        logger.info(f"🔑 Granting admin access to owner: {instance.user.username} @ {instance.tenant.slug}")
        instance.user.is_staff = True
        instance.user.save(update_fields=['is_staff'])
        logger.info(f"✅ Admin access granted to {instance.user.username}")

