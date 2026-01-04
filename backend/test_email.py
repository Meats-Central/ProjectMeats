#!/usr/bin/env python
"""
Test script to verify SendGrid email configuration.
Run: python test_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.production')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Display email configuration."""
    print("=" * 60)
    print("EMAIL CONFIGURATION")
    print("=" * 60)
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'✅ SET' if settings.EMAIL_HOST_PASSWORD else '❌ NOT SET'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("=" * 60)

def test_send_email(recipient_email):
    """Send a test email."""
    print(f"\n📧 Sending test email to: {recipient_email}")
    
    try:
        result = send_mail(
            subject="🧪 Test Email from Project Meats",
            message="This is a test email to verify SendGrid integration.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Email sent successfully!")
            return True
        else:
            print(f"⚠️ Email send returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send email: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_config()
    
    # Check if email password is set
    if not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: EMAIL_HOST_PASSWORD is not set!")
        print("Set the environment variable before running this test:")
        print("export EMAIL_HOST_PASSWORD='your-sendgrid-api-key'")
        exit(1)
    
    # Prompt for test recipient
    recipient = input("\nEnter recipient email address for test: ").strip()
    if recipient and '@' in recipient:
        test_send_email(recipient)
    else:
        print("❌ Invalid email address")
