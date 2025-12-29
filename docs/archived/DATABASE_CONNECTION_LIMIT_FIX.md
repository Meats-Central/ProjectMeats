# Database Connection Limit Error - Fix Required

**Date:** December 7, 2025  
**Status:** ⚠️ **DEPLOYMENT BLOCKED**  
**Error:** `FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute`

---

## 🔍 Problem

The DigitalOcean managed PostgreSQL database has **run out of available connections**.

**Error Message:**
```
psycopg.OperationalError: connection failed: connection to server at "165.22.35.208", port 25060 failed: 
FATAL:  remaining connection slots are reserved for roles with the SUPERUSER attribute
```

### Root Cause

1. **Small database plan** has limited connections (likely 25 connections on Basic plan)
2. **Multiple deployment attempts** left connections open
3. **Connection pooling (CONN_MAX_AGE=600)** keeps connections alive for 10 minutes
4. **No automatic connection cleanup**

---

## ✅ Immediate Fix (Close Idle Connections)

### Option 1: Via DigitalOcean Console (Recommended)

1. Go to https://cloud.digitalocean.com/databases
2. Find your PostgreSQL database
3. Click "Users & Databases"
4. Click on "Connection Pools" tab
5. Create a connection pool with these settings:
   - **Pool Mode:** Transaction
   - **Pool Size:** 20
   - **Database:** Your database name
   - **User:** Your database user

6. Update `DATABASE_URL` secret to use the **pool connection string** instead of direct connection

### Option 2: Manually Kill Connections

**SSH to backend server:**
```bash
ssh django@157.245.114.182
```

**Run PostgreSQL query to kill idle connections:**
```bash
# Using psql (if available)
PGPASSWORD='your-password' psql -h 165.22.35.208 -p 25060 -U your-user -d your-database -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND pid <> pg_backend_pid();"
```

**Or use Django management command:**
```bash
cd /home/django/ProjectMeats/backend
source venv/bin/activate
python manage.py shell << 'PYTHON'
from django.db import connection
connection.close()
print("Connection closed")
PYTHON
```

### Option 3: Restart Database (Last Resort)

1. Go to DigitalOcean console
2. Find your database
3. Click "Settings"
4. Click "Restart" (WARNING: Brief downtime)

---

## 🔧 Long-Term Solutions

### 1. Reduce CONN_MAX_AGE (Quick Fix)

Edit `backend/projectmeats/settings/production.py`:

```python
# Current (keeps connections for 10 minutes)
conn_max_age=600,

# Change to (keeps connections for 1 minute)
conn_max_age=60,
```

### 2. Use Connection Pooling (Recommended)

**Add PgBouncer via DigitalOcean:**
1. Create connection pool in DigitalOcean console
2. Use pool connection string instead of direct database URL
3. Benefits:
   - Reuses connections
   - Limits max connections
   - No code changes needed

### 3. Upgrade Database Plan

**Current Plan (assumed):** Basic - 25 connections  
**Upgrade to:** Professional - 97 connections

Cost: ~$55/month → ~$110/month

### 4. Close Connections After Migrations

Update workflow to close connections after migrations:

```yaml
# In .github/workflows/11-dev-deployment.yml
- name: Run migrations
  run: |
    python manage.py migrate --fake-initial --noinput
    python manage.py shell -c "from django.db import connection; connection.close()"
```

---

## 🚀 Immediate Action Required

**To unblock deployment RIGHT NOW:**

1. **Go to DigitalOcean Console**
   - Navigate to your database
   - Restart it (Settings → Restart)
   - Wait 2 minutes

2. **Re-run Deployment**
   ```bash
   gh workflow run 11-dev-deployment.yml --ref development
   ```

3. **Monitor Connections**
   - After successful deployment, monitor connection count
   - Implement long-term fix before next deployment

---

## 📊 Check Current Connection Count

```sql
SELECT count(*) FROM pg_stat_activity;
```

**If result is close to your plan limit (e.g., 23/25), implement fixes above.**

---

## 🎯 Recommended Immediate Steps

1. ✅ **Restart database in DigitalOcean console** (5 minutes)
2. ✅ **Re-deploy** (deployment should work with fresh connections)
3. ⏰ **Set up connection pool** in DigitalOcean (after successful deployment)
4. ⏰ **Reduce CONN_MAX_AGE to 60** in next PR

---

## 📞 Support

If database restart doesn't work:
1. Check database logs in DigitalOcean console
2. Verify DATABASE_URL secret is correct
3. Try manual connection from backend server
4. Consider upgrading database plan temporarily

---

**Status:** Database connection limit reached - restart database and redeploy
