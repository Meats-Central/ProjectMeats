#!/bin/bash
# Server-Side Email Diagnostic Script
# Run this on your server to diagnose invitation email issues

echo "============================================================"
echo "📧 ProjectMeats Email Diagnostic Tool"
echo "============================================================"
echo ""

# Check if running in Docker container or host
if [ -f /.dockerenv ]; then
    echo "✅ Running inside Docker container"
    DOCKER_PREFIX=""
else
    echo "⚠️  Running on host - will use docker exec"
    DOCKER_PREFIX="docker exec pm-backend"
fi

echo ""
echo "1️⃣  CHECKING ENVIRONMENT VARIABLES"
echo "------------------------------------------------------------"

# Check email-related environment variables
$DOCKER_PREFIX printenv | grep -E "EMAIL|SMTP|SENDGRID|DEFAULT_FROM" | while read line; do
    # Mask password values
    if echo "$line" | grep -q "PASSWORD"; then
        key=$(echo "$line" | cut -d= -f1)
        value=$(echo "$line" | cut -d= -f2)
        if [ -n "$value" ]; then
            echo "✅ $key=***SET*** (${#value} characters)"
        else
            echo "❌ $key=NOT_SET"
        fi
    else
        echo "✅ $line"
    fi
done

echo ""
echo "2️⃣  CHECKING DJANGO EMAIL SETTINGS"
echo "------------------------------------------------------------"

$DOCKER_PREFIX python manage.py shell -c "
from django.conf import settings
import os

print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_HOST:', settings.EMAIL_HOST)
print('EMAIL_PORT:', settings.EMAIL_PORT)
print('EMAIL_USE_TLS:', settings.EMAIL_USE_TLS)
print('EMAIL_HOST_USER:', settings.EMAIL_HOST_USER)

password = settings.EMAIL_HOST_PASSWORD
if password:
    print(f'EMAIL_HOST_PASSWORD: ✅ SET ({len(password)} chars)')
    # Show first/last 3 chars to verify correct secret
    if len(password) > 10:
        print(f'  Starts with: {password[:3]}...')
        print(f'  Ends with: ...{password[-3:]}')
else:
    print('EMAIL_HOST_PASSWORD: ❌ NOT SET')

print('DEFAULT_FROM_EMAIL:', settings.DEFAULT_FROM_EMAIL)

# Check if using production settings
print()
print('DJANGO_SETTINGS_MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET'))
"

echo ""
echo "3️⃣  CHECKING .ENV FILE (if exists)"
echo "------------------------------------------------------------"

if [ -f /root/projectmeats/backend/.env ]; then
    echo "✅ .env file found at /root/projectmeats/backend/.env"
    grep -E "EMAIL|SMTP|SENDGRID|DEFAULT_FROM" /root/projectmeats/backend/.env | while read line; do
        if echo "$line" | grep -q "PASSWORD"; then
            key=$(echo "$line" | cut -d= -f1)
            echo "  $key=***MASKED***"
        else
            echo "  $line"
        fi
    done
else
    echo "⚠️  No .env file found at /root/projectmeats/backend/.env"
    echo "   (This is OK if using environment variables directly)"
fi

echo ""
echo "4️⃣  TESTING SMTP CONNECTION"
echo "------------------------------------------------------------"

$DOCKER_PREFIX python manage.py shell -c "
from django.core.mail import get_connection
from django.conf import settings
import socket

print('Attempting to connect to SMTP server...')
print(f'Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')

try:
    # Test basic socket connection first
    sock = socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=10)
    print('✅ Socket connection successful')
    sock.close()
    
    # Test SMTP connection with Django
    conn = get_connection()
    result = conn.open()
    if result:
        print('✅ SMTP authentication successful')
        conn.close()
    else:
        print('❌ SMTP authentication failed - check API key')
except socket.timeout:
    print('❌ Connection timeout - firewall may be blocking port 587')
except socket.gaierror as e:
    print(f'❌ DNS resolution failed: {e}')
except Exception as e:
    print(f'❌ Connection failed: {type(e).__name__}: {e}')
"

echo ""
echo "5️⃣  CHECKING SIGNAL REGISTRATION"
echo "------------------------------------------------------------"

$DOCKER_PREFIX python manage.py shell -c "
from django.db.models import signals
from apps.tenants.models import TenantInvitation

# Check if signal is registered
receivers = signals.post_save._live_receivers(TenantInvitation)
receiver_list = list(receivers)

print(f'Registered post_save receivers for TenantInvitation: {len(receiver_list)}')

if receiver_list:
    print('✅ Signal handler is CONNECTED')
    for i, receiver in enumerate(receiver_list, 1):
        if receiver:
            func = receiver[1] if isinstance(receiver, tuple) else receiver
            print(f'  {i}. {func}')
else:
    print('❌ Signal handler is NOT CONNECTED - emails will not send!')
"

echo ""
echo "6️⃣  CHECKING RECENT INVITATION ACTIVITY"
echo "------------------------------------------------------------"

$DOCKER_PREFIX python manage.py shell -c "
from apps.tenants.models import TenantInvitation
from django.utils import timezone
from datetime import timedelta

recent_cutoff = timezone.now() - timedelta(hours=24)
recent_invitations = TenantInvitation.objects.filter(
    created_at__gte=recent_cutoff
).order_by('-created_at')[:5]

if recent_invitations:
    print(f'Found {recent_invitations.count()} invitations in last 24 hours:')
    for inv in recent_invitations:
        print(f'  - {inv.email or \"(no email)\"} | {inv.status} | {inv.created_at}')
else:
    print('No invitations created in last 24 hours')
"

echo ""
echo "7️⃣  CHECKING DOCKER LOGS FOR EMAIL ACTIVITY"
echo "------------------------------------------------------------"

if [ -z "$DOCKER_PREFIX" ]; then
    echo "Searching container logs for email-related messages..."
    docker logs pm-backend --tail 100 2>&1 | grep -E "📧|email|invitation|send_mail" | tail -20
else
    echo "⚠️  Cannot check logs from inside container"
    echo "   Run 'docker logs pm-backend --tail 100 | grep 📧' on host"
fi

echo ""
echo "============================================================"
echo "🔍 DIAGNOSTIC COMPLETE"
echo "============================================================"
echo ""
echo "Next steps based on results:"
echo ""
echo "If EMAIL_HOST_PASSWORD is NOT SET:"
echo "  → Set GitHub secret: gh secret set EMAIL_HOST_PASSWORD --env <env>-backend"
echo "  → Redeploy the application"
echo ""
echo "If SMTP connection fails:"
echo "  → Check firewall rules for outbound port 587"
echo "  → Verify SendGrid API key is valid"
echo "  → Try alternative ports: 2525 or 465 (SSL)"
echo ""
echo "If signal NOT CONNECTED:"
echo "  → Check apps.tenants.signals is imported in apps.py"
echo "  → Restart Django application"
echo ""
echo "If everything looks good but emails don't send:"
echo "  → Check SendGrid activity log: https://app.sendgrid.com/activity"
echo "  → Verify sender email is verified in SendGrid"
echo "  → Check spam folder of recipient"
echo ""
