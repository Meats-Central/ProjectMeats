# Staging Load Failure Fix - Quick Start Guide

## 🎯 What This PR Does
Fixes the persistent load failure on `staging.meatscentral.com` by adding debug logging, fixing configuration, and providing tools for diagnosis and resolution.

## 🚀 Quick Deploy

### 1️⃣ Deploy the Code
```bash
# Already done if you're reading this in the branch
git checkout copilot/debug-staging-load-failure
git pull
```

### 2️⃣ Add Domain Entry (One-Time Setup)
```bash
# SSH to staging server
ssh staging.meatscentral.com

# Run management command
cd /path/to/projectmeats/backend
python manage.py add_tenant_domain \
    --domain=staging.meatscentral.com \
    --tenant-slug=meatscentral
```

### 3️⃣ Restart Application
```bash
sudo systemctl restart projectmeats
# OR
docker-compose restart web
# OR
kubectl rollout restart deployment/projectmeats-backend
```

### 4️⃣ Test It
Open browser → Navigate to `https://staging.meatscentral.com`

Should see: ✅ Application loads successfully

### 5️⃣ Verify Logs (Optional)
```bash
tail -f /var/log/django.log | grep "STAGING DEBUG"
```

Expected output:
```
INFO [STAGING DEBUG] Request received - host=staging.meatscentral.com ...
INFO [STAGING DEBUG] Tenant resolved via domain - tenant=meatscentral ...
INFO [STAGING DEBUG] Final tenant resolution SUCCESS ...
```

### 6️⃣ Cleanup (After Verification)
```bash
# From repository root
python3 remove_debug_logging.py
git add backend/apps/tenants/middleware.py
git commit -m "Remove temporary staging debug logging"
git push
```

## 📋 What Changed

### Fixed
- ✅ Added `staging.meatscentral.com` to `ALLOWED_HOSTS`
- ✅ Added debug logging to diagnose tenant resolution
- ✅ Created management command to add domain entries

### Added Tools
- 🔧 `add_tenant_domain` - Management command to add/update domains
- 🔍 `verify_staging_config.py` - Validate configuration
- 🧹 `remove_debug_logging.py` - Clean up after verification

### Added Documentation
- 📖 `STAGING_LOAD_FAILURE_FIX.md` - Full deployment guide
- 📖 `IMPLEMENTATION_SUMMARY_STAGING_FIX.md` - Technical details
- 📖 `SECURITY_SUMMARY_STAGING_FIX.md` - Security analysis

## 🔍 Troubleshooting

### Problem: "Domain entry not created"
**Solution:**
```bash
# List available tenants
python manage.py shell -c "from apps.tenants.models import Tenant; \
    print(*Tenant.objects.values_list('slug', 'name'), sep='\n')"

# Use correct tenant slug in command
```

### Problem: "Still getting 404"
**Solution:**
```bash
# Verify configuration
python3 verify_staging_config.py
```

### Problem: "No debug logs showing"
**Solution:**
Check logging level in settings - must be INFO or DEBUG

## 📚 More Information

- **Full Deployment Guide:** [STAGING_LOAD_FAILURE_FIX.md](STAGING_LOAD_FAILURE_FIX.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY_STAGING_FIX.md](IMPLEMENTATION_SUMMARY_STAGING_FIX.md)
- **Security Analysis:** [SECURITY_SUMMARY_STAGING_FIX.md](SECURITY_SUMMARY_STAGING_FIX.md)

## ✅ Success Checklist

- [ ] Code deployed to staging
- [ ] Domain entry created (via management command)
- [ ] Application restarted
- [ ] staging.meatscentral.com loads in browser
- [ ] Users can log in successfully
- [ ] Debug logs show successful tenant resolution
- [ ] Cleanup script run to remove debug logging

## 🆘 Need Help?

1. Check [STAGING_LOAD_FAILURE_FIX.md](STAGING_LOAD_FAILURE_FIX.md) troubleshooting section
2. Run `python3 verify_staging_config.py` to diagnose issues
3. Check application logs for `[STAGING DEBUG]` entries
4. Verify database has active tenant with slug "meatscentral"

## 📝 Notes

- Debug logging is **temporary** - remove after verification
- Only activates for `staging.meatscentral.com` (not production)
- Management command is **permanent** - useful for other domains too
- Tests included in `backend/apps/tenants/test_middleware_debug.py`
