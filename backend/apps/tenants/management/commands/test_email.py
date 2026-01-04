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
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        
        password_status = '✅ SET' if settings.EMAIL_HOST_PASSWORD else '❌ NOT SET'
        password_length = len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 0
        self.stdout.write(f"  EMAIL_HOST_PASSWORD: {password_status} ({password_length} characters)")
        
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Check for issues
        issues = []
        if not settings.EMAIL_HOST_PASSWORD:
            issues.append("❌ EMAIL_HOST_PASSWORD is not set")
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
        
        if not settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(self.style.ERROR("\n❌ Cannot send email: EMAIL_HOST_PASSWORD not set"))
            sys.exit(1)
        
        self.stdout.write(f"\n📤 Sending test email to: {recipient}")
        
        try:
            result = send_mail(
                subject="🧪 Test Email from Project Meats",
                message=(
                    "This is a test email to verify SendGrid integration.\n\n"
                    "If you receive this email, your SendGrid configuration is working correctly!\n\n"
                    "Email Settings:\n"
                    f"- Backend: {settings.EMAIL_BACKEND}\n"
                    f"- Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}\n"
                    f"- From: {settings.DEFAULT_FROM_EMAIL}\n"
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
            self.stdout.write("  1. Verify EMAIL_HOST_PASSWORD is your SendGrid API key")
            self.stdout.write("  2. Check that sender email is verified in SendGrid")
            self.stdout.write("  3. Ensure SendGrid API key has 'Mail Send' permissions")
            self.stdout.write("  4. Check SendGrid activity log for more details")
            
            sys.exit(1)
