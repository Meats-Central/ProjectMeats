"""
Tests for tenant invitation email functionality.
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from apps.tenants.models import Tenant, TenantUser, TenantInvitation
from apps.tenants.email_utils import send_invitation_email


class InvitationEmailTests(TestCase):
    """Test cases for invitation email sending."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User"
        )
        
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="contact@testcompany.com",
            created_by=self.user,
        )
        
        TenantUser.objects.create(
            tenant=self.tenant,
            user=self.user,
            role="admin",
            is_active=True
        )
    
    def test_send_invitation_email_success(self):
        """Test that invitation email is sent successfully."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="newuser@test.com",
            role="manager",
            invited_by=self.user,
            message="Welcome to the team!",
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Send email
        result = send_invitation_email(invitation)
        
        # Check result
        self.assertTrue(result)
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email details
        email = mail.outbox[0]
        self.assertEqual(email.to, ["newuser@test.com"])
        self.assertIn("Test Company", email.subject)
        self.assertIn("ProjectMeats", email.subject)
        
        # Check email body contains important info
        self.assertIn("Test Company", email.body)
        self.assertIn("Manager", email.body)
        self.assertIn("Admin User", email.body)
        self.assertIn("Welcome to the team!", email.body)
        self.assertIn(invitation.token, email.body)
        
        # Check HTML version exists
        self.assertIsNotNone(email.alternatives)
        self.assertEqual(len(email.alternatives), 1)
        html_content = email.alternatives[0][0]
        self.assertIn("Test Company", html_content)
        self.assertIn(invitation.token, html_content)
    
    def test_send_invitation_email_without_inviter(self):
        """Test email sending when no inviter is set."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="newuser@test.com",
            role="user",
            invited_by=None,  # No inviter
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        result = send_invitation_email(invitation)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        # Should still send, but without inviter name
        self.assertIn("Test Company", email.body)
        self.assertNotIn("Admin User", email.body)
    
    def test_send_invitation_email_without_message(self):
        """Test email sending when no message is provided."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="newuser@test.com",
            role="user",
            invited_by=self.user,
            message="",  # Empty message
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        result = send_invitation_email(invitation)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(FRONTEND_URL="https://custom.example.com")
    def test_send_invitation_email_custom_frontend_url(self):
        """Test that custom FRONTEND_URL is used in email."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="newuser@test.com",
            role="user",
            invited_by=self.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        result = send_invitation_email(invitation)
        
        self.assertTrue(result)
        email = mail.outbox[0]
        self.assertIn("https://custom.example.com/signup?token=", email.body)


class InvitationEmailAPITests(APITestCase):
    """Test cases for email sending via API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123"
        )
        
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="contact@testcompany.com",
            created_by=self.admin_user,
        )
        
        TenantUser.objects.create(
            tenant=self.tenant,
            user=self.admin_user,
            role="admin",
            is_active=True
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_invitation_sends_email(self):
        """Test that creating invitation via API sends email."""
        from django.urls import reverse
        
        url = reverse('tenants:tenant-invitation-list')
        data = {
            'email': 'newuser@test.com',
            'role': 'manager',
            'message': 'Join us!'
        }
        
        # Clear mail outbox
        mail.outbox = []
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['newuser@test.com'])
        self.assertIn('Test Company', email.subject)
    
    def test_resend_invitation_sends_email(self):
        """Test that resending invitation via API sends email."""
        from django.urls import reverse
        
        # Create invitation first
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email='newuser@test.com',
            role='user',
            invited_by=self.admin_user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Clear mail outbox (invitation creation already sent one)
        mail.outbox = []
        
        url = reverse('tenants:tenant-invitation-resend', kwargs={'pk': invitation.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['newuser@test.com'])
        
        # Check expiration was extended
        invitation.refresh_from_db()
        self.assertGreater(invitation.expires_at, timezone.now() + timedelta(days=6))
    
    def test_create_multiple_invitations_sends_multiple_emails(self):
        """Test that creating multiple invitations sends multiple emails."""
        from django.urls import reverse
        
        url = reverse('tenants:tenant-invitation-list')
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create first invitation
        data1 = {'email': 'user1@test.com', 'role': 'user'}
        response1 = self.client.post(url, data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Create second invitation
        data2 = {'email': 'user2@test.com', 'role': 'manager'}
        response2 = self.client.post(url, data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Check two emails were sent
        self.assertEqual(len(mail.outbox), 2)
        emails = [email.to[0] for email in mail.outbox]
        self.assertIn('user1@test.com', emails)
        self.assertIn('user2@test.com', emails)


class InvitationAdminEmailTests(TestCase):
    """Test cases for email sending via Django admin."""
    
    def setUp(self):
        """Set up test fixtures."""
        from django.contrib.admin.sites import AdminSite
        from apps.tenants.admin import TenantInvitationAdmin
        
        self.admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@test.com",
            password="testpass123"
        )
        
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="contact@testcompany.com",
            created_by=self.admin_user,
        )
        
        self.site = AdminSite()
        self.admin = TenantInvitationAdmin(TenantInvitation, self.site)
    
    def test_admin_save_model_sends_email(self):
        """Test that admin save_model sends email for new invitations."""
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create a mock request with message storage
        request = RequestFactory().get('/')
        request.user = self.admin_user
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)
        
        # Create invitation instance
        invitation = TenantInvitation(
            tenant=self.tenant,
            email='newuser@test.com',
            role='manager',
            message='Welcome!',
            status='pending',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Mock form (not used but required by signature)
        from django import forms
        form = forms.Form()
        
        # Save via admin
        self.admin.save_model(request, invitation, form, change=False)
        
        # Check invitation was saved
        self.assertIsNotNone(invitation.id)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['newuser@test.com'])
    
    def test_admin_resend_action_sends_emails(self):
        """Test that resend admin action sends emails."""
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        
        # Create invitations
        invitation1 = TenantInvitation.objects.create(
            tenant=self.tenant,
            email='user1@test.com',
            role='user',
            invited_by=self.admin_user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        invitation2 = TenantInvitation.objects.create(
            tenant=self.tenant,
            email='user2@test.com',
            role='manager',
            invited_by=self.admin_user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create a mock request with message storage
        request = RequestFactory().get('/')
        request.user = self.admin_user
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)
        
        # Create queryset
        queryset = TenantInvitation.objects.filter(
            id__in=[invitation1.id, invitation2.id]
        )
        
        # Call resend action
        self.admin.resend_invitation_emails(request, queryset)
        
        # Check emails were sent
        self.assertEqual(len(mail.outbox), 2)
        emails = [email.to[0] for email in mail.outbox]
        self.assertIn('user1@test.com', emails)
        self.assertIn('user2@test.com', emails)
