"""
Tests for Celery email tasks.

Tests the asynchronous email sending functionality for tenant invitations.
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from apps.tenants.models import Tenant, TenantInvitation
from apps.tenants.tasks import (
    send_invitation_email,
    cleanup_expired_invitations,
    send_bulk_invitations
)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,  # Execute tasks synchronously in tests
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class InvitationEmailTaskTestCase(TestCase):
    """Test invitation email sending tasks."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            is_active=True
        )
        
        # Create a valid invitation
        self.invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email='testuser@example.com',
            role='admin',
            invited_by=None,
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True,
            is_used=False
        )

    def test_send_invitation_email_success(self):
        """Test successful invitation email sending."""
        # Clear the test outbox
        mail.outbox = []
        
        # Send invitation email
        result = send_invitation_email(self.invitation.id)
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['email'], self.invitation.email)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        
        # Verify email contents
        self.assertIn(self.tenant.name, sent_email.subject)
        self.assertEqual(sent_email.to, [self.invitation.email])
        self.assertIn(str(self.invitation.token), sent_email.body)
        self.assertIn('admin', sent_email.body.lower())

    def test_send_invitation_email_expired(self):
        """Test that expired invitations are skipped."""
        # Create expired invitation
        expired_invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email='expired@example.com',
            role='member',
            expires_at=timezone.now() - timedelta(days=1),
            is_active=True,
            is_used=False
        )
        
        mail.outbox = []
        
        # Try to send email
        result = send_invitation_email(expired_invitation.id)
        
        # Verify it was skipped
        self.assertEqual(result['status'], 'skipped')
        self.assertIn('expired', result['reason'].lower())
        
        # Verify no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_send_invitation_email_inactive(self):
        """Test that inactive invitations are skipped."""
        self.invitation.is_active = False
        self.invitation.save()
        
        mail.outbox = []
        
        # Try to send email
        result = send_invitation_email(self.invitation.id)
        
        # Verify it was skipped
        self.assertEqual(result['status'], 'skipped')
        
        # Verify no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_send_invitation_email_already_used(self):
        """Test that used invitations are skipped."""
        self.invitation.is_used = True
        self.invitation.save()
        
        mail.outbox = []
        
        # Try to send email
        result = send_invitation_email(self.invitation.id)
        
        # Verify it was skipped
        self.assertEqual(result['status'], 'skipped')
        
        # Verify no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_send_invitation_email_html_content(self):
        """Test that HTML email is sent with proper formatting."""
        mail.outbox = []
        
        # Send invitation email
        send_invitation_email(self.invitation.id)
        
        # Verify HTML alternative exists
        sent_email = mail.outbox[0]
        self.assertTrue(hasattr(sent_email, 'alternatives'))
        self.assertTrue(len(sent_email.alternatives) > 0)
        
        # Verify HTML content
        html_content = sent_email.alternatives[0][0]
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn(str(self.invitation.token), html_content)
        self.assertIn(self.tenant.name, html_content)


class CleanupTaskTestCase(TestCase):
    """Test cleanup tasks."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            is_active=True
        )

    def test_cleanup_expired_invitations(self):
        """Test cleanup of expired invitations."""
        # Create expired invitations
        for i in range(3):
            TenantInvitation.objects.create(
                tenant=self.tenant,
                email=f'expired{i}@example.com',
                role='member',
                expires_at=timezone.now() - timedelta(days=i+1),
                is_active=True,
                is_used=False
            )
        
        # Create valid invitation (should not be cleaned up)
        TenantInvitation.objects.create(
            tenant=self.tenant,
            email='valid@example.com',
            role='member',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True,
            is_used=False
        )
        
        # Run cleanup task
        result = cleanup_expired_invitations()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['count'], 3)
        
        # Verify expired invitations are deactivated
        expired_count = TenantInvitation.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        ).count()
        self.assertEqual(expired_count, 0)
        
        # Verify valid invitation is still active
        valid_count = TenantInvitation.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        self.assertEqual(valid_count, 1)


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class BulkInvitationTaskTestCase(TestCase):
    """Test bulk invitation sending."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            is_active=True
        )

    @patch('apps.tenants.tasks.send_invitation_email.delay')
    def test_send_bulk_invitations(self, mock_send):
        """Test sending multiple invitations in bulk."""
        # Create multiple invitations
        invitation_ids = []
        for i in range(5):
            invitation = TenantInvitation.objects.create(
                tenant=self.tenant,
                email=f'user{i}@example.com',
                role='member',
                expires_at=timezone.now() + timedelta(days=7),
                is_active=True,
                is_used=False
            )
            invitation_ids.append(invitation.id)
        
        # Mock the delay method to return success
        mock_send.return_value = MagicMock()
        
        # Send bulk invitations
        result = send_bulk_invitations(invitation_ids)
        
        # Verify all were queued
        self.assertEqual(result['success'], 5)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(mock_send.call_count, 5)
