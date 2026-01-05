"""
Management command to test SendGrid email configuration.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test SendGrid email configuration and send a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Recipient email address for test email',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check configuration without sending email',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("📧 SendGrid Email Configuration Test"))
        self.stdout.write("=" * 60)
        
        # Display configuration
        self.stdout.write("\n🔧 Current Configuration:")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        api_key_status = '✅ SET' if api_key else '❌ NOT SET'
        api_key_length = len(api_key) if api_key else 0
        self.stdout.write(f"  SENDGRID_API_KEY: {api_key_status} ({api_key_length} characters)")
        
        sandbox_mode = getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', False)
        self.stdout.write(f"  SENDGRID_SANDBOX_MODE_IN_DEBUG: {sandbox_mode}")
        
        # Check for issues
        issues = []
        if not api_key:
            issues.append("❌ SENDGRID_API_KEY is not set")
        if not settings.DEFAULT_FROM_EMAIL:
            issues.append("❌ DEFAULT_FROM_EMAIL is not set")
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            issues.append("⚠️  EMAIL_BACKEND is set to console (emails won't be sent)")
        
        if issues:
            self.stdout.write("\n⚠️  Configuration Issues:")
            for issue in issues:
                self.stdout.write(f"  {issue}")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Configuration looks good!"))
        
        # Stop here if check-only
        if options['check_only']:
            return
        
        # Send test email
        recipient = options['to']
        if not recipient:
            self.stdout.write("\n❌ No recipient specified. Use --to=email@example.com")
            sys.exit(1)
        
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if not api_key:
            self.stdout.write(self.style.ERROR("\n❌ Cannot send email: SENDGRID_API_KEY not set"))
            sys.exit(1)
        
        self.stdout.write(f"\n📤 Sending test email to: {recipient}")
        
        try:
            result = send_mail(
                subject="🧪 Test Email from Project Meats",
                message=(
                    "This is a test email to verify SendGrid Web API integration.\n\n"
                    "If you receive this email, your SendGrid configuration is working correctly!\n\n"
                    "Email Settings:\n"
                    f"- Backend: {settings.EMAIL_BACKEND}\n"
                    f"- From: {settings.DEFAULT_FROM_EMAIL}\n"
                    f"- API: SendGrid Web API v3\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(self.style.SUCCESS("\n✅ Test email sent successfully!"))
                self.stdout.write("Check your inbox (and spam folder) for the test email.")
            else:
                self.stdout.write(self.style.WARNING(f"\n⚠️  Email send returned: {result}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to send email: {type(e).__name__}"))
            self.stdout.write(self.style.ERROR(f"   {str(e)}"))
            
            # Provide troubleshooting tips
            self.stdout.write("\n🔍 Troubleshooting Tips:")
            self.stdout.write("  1. Verify SENDGRID_API_KEY is your SendGrid API key")
            self.stdout.write("  2. Check that sender email (no-reply@meatscentral.com) is verified in SendGrid")
            self.stdout.write("  3. Ensure SendGrid API key has 'Mail Send' permissions")
            self.stdout.write("  4. Check SendGrid activity log for more details")
            
            sys.exit(1)
