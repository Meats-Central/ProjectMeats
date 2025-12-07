"""
Celery tasks for tenant management.

This module contains asynchronous tasks for tenant-related operations,
including invitation email sending and cleanup tasks.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invitation_email(self, invitation_id):
    """
    Send invitation email asynchronously.
    
    Args:
        invitation_id: ID of the TenantInvitation to send
        
    Returns:
        dict: Status information about the email send
    """
    try:
        from apps.tenants.models import TenantInvitation
        
        invitation = TenantInvitation.objects.get(id=invitation_id)
        
        # Check if invitation is still valid
        if not invitation.is_active or invitation.is_used:
            logger.warning(
                f"Attempted to send email for inactive/used invitation: {invitation_id}"
            )
            return {
                'status': 'skipped',
                'reason': 'Invitation is not active or already used'
            }
        
        # Check if invitation has expired
        if invitation.expires_at and invitation.expires_at < timezone.now():
            logger.warning(
                f"Attempted to send email for expired invitation: {invitation_id}"
            )
            return {
                'status': 'skipped',
                'reason': 'Invitation has expired'
            }
        
        # Build invitation URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        invitation_url = f"{frontend_url}/accept-invitation/{invitation.token}"
        
        # Email content
        subject = f"Invitation to join {invitation.tenant.name} on ProjectMeats"
        
        message = f"""
Hello,

You have been invited to join {invitation.tenant.name} on ProjectMeats.

Your role: {invitation.role.upper()}

To accept this invitation, please click the link below:
{invitation_url}

This invitation will expire on {invitation.expires_at.strftime('%Y-%m-%d %H:%M UTC') if invitation.expires_at else 'never'}.

If you did not expect this invitation, you can safely ignore this email.

Best regards,
The ProjectMeats Team
"""
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2c5282; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f7fafc; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #3182ce; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #718096; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ProjectMeats Invitation</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            
            <p>You have been invited to join <strong>{invitation.tenant.name}</strong> on ProjectMeats.</p>
            
            <p><strong>Your role:</strong> {invitation.role.upper()}</p>
            
            <p>To accept this invitation, please click the button below:</p>
            
            <a href="{invitation_url}" class="button">Accept Invitation</a>
            
            <p><small>Or copy and paste this link into your browser:<br>
            {invitation_url}</small></p>
            
            <p><em>This invitation will expire on {invitation.expires_at.strftime('%Y-%m-%d %H:%M UTC') if invitation.expires_at else 'never'}.</em></p>
            
            <p>If you did not expect this invitation, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The ProjectMeats Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        
        logger.info(f"Successfully sent invitation email to {invitation.email}")
        
        return {
            'status': 'success',
            'email': invitation.email,
            'invitation_id': str(invitation_id)
        }
        
    except Exception as exc:
        logger.error(
            f"Error sending invitation email for {invitation_id}: {exc}",
            exc_info=True
        )
        # Retry the task
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_invitations():
    """
    Periodic task to clean up expired invitations.
    
    This task runs daily (configured in celery.py beat_schedule) to
    deactivate expired invitations that are still marked as active.
    
    Returns:
        dict: Count of invitations cleaned up
    """
    try:
        from apps.tenants.models import TenantInvitation
        
        # Find expired invitations that are still active
        now = timezone.now()
        expired_invitations = TenantInvitation.objects.filter(
            is_active=True,
            is_used=False,
            expires_at__lt=now
        )
        
        count = expired_invitations.count()
        
        # Deactivate them
        expired_invitations.update(is_active=False)
        
        logger.info(f"Cleaned up {count} expired invitations")
        
        return {
            'status': 'success',
            'count': count
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up expired invitations: {exc}", exc_info=True)
        return {
            'status': 'error',
            'error': str(exc)
        }


@shared_task(bind=True, max_retries=3)
def send_bulk_invitations(self, invitation_ids):
    """
    Send multiple invitation emails in bulk.
    
    Args:
        invitation_ids: List of invitation IDs to send
        
    Returns:
        dict: Summary of sent emails
    """
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }
    
    for invitation_id in invitation_ids:
        try:
            result = send_invitation_email.delay(invitation_id)
            # Note: This returns AsyncResult, actual status will be in result backend
            results['success'] += 1
        except Exception as exc:
            logger.error(f"Error queuing invitation {invitation_id}: {exc}")
            results['failed'] += 1
            results['errors'].append({
                'invitation_id': str(invitation_id),
                'error': str(exc)
            })
    
    return results
