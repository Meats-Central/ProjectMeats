# GitHub Actions Database Access Setup for DigitalOcean

**Created:** 2025-12-04  
**Issue:** GitHub Actions cannot connect to DigitalOcean managed database  
**Error:** `psycopg2.OperationalError: connection timeout expired`

---

## Problem

GitHub Actions runners need to connect to your DigitalOcean managed PostgreSQL database to run migrations during deployment. Currently, the connection times out because DigitalOcean databases restrict access to trusted sources only.

**Error in Logs:**
```
psycopg2.OperationalError: connection to server at 
"meatscentral-dev-db-do-user-24316406-0.k.db.ondigitalocean.com" (159.203.75.143), 
port 25060 failed: timeout expired
```

---

## Solution Options

There are **two approaches** to solve this:

### Option 1: Add GitHub Actions IP Ranges (Recommended for CI/CD)
### Option 2: Use SSH Tunnel via Deployment Server

---

## Option 1: Add GitHub Actions IP Ranges to Trusted Sources

### Important Limitation

⚠️ **GitHub Actions does not provide a fixed list of IP addresses.** The IP addresses used by GitHub-hosted runners change frequently. 

**From GitHub Documentation:**
> "GitHub Actions hosted runners IP addresses are not static and may change over time. We do not recommend IP allow-listing for GitHub Actions."

### Alternative: Allow All IPs (Development Only)

For **development environment only**, you can temporarily allow all IPs:

#### Steps:

1. **Go to DigitalOcean Console:**
   - Navigate to: https://cloud.digitalocean.com/databases
   - Click on your database cluster

2. **Select "Settings" Tab:**
   - Scroll to "Trusted Sources" section

3. **Add "All IPv4 Addresses" (TEMPORARY):**
   - Click "Edit"
   - Click "Add trusted source"
   - Select "All IPv4 addresses (0.0.0.0/0)"
   - Add description: "GitHub Actions CI - TEMPORARY"
   - Click "Save"

4. **Security Warning:**
   ```
   ⚠️ This makes your database accessible from anywhere on the internet.
   ⚠️ Only do this for development databases.
   ⚠️ Never do this for production databases.
   ⚠️ Make sure your database password is very strong.
   ⚠️ Monitor your database access logs.
   ```

#### Better Alternative for Development:

Instead of 0.0.0.0/0, use GitHub Actions IP ranges (documented approach):

**GitHub provides these IP ranges** (as of 2025-12-04):
- You can get current ranges from: https://api.github.com/meta

Let me create a script to fetch and add these ranges:

---

## Option 2: Use SSH Tunnel (Recommended for Production)

This is the **recommended approach** for production and UAT environments.

### How It Works:

```
GitHub Actions → SSH to Deployment Server → Database Connection
```

The deployment server (where your app runs) already has database access. We run migrations through it.

### Implementation:

#### Current Workflow (runs migrations in CI):
```yaml
# ❌ This fails because GitHub Actions can't reach database
- name: Run idempotent migrations
  run: python manage.py migrate
```

#### Updated Workflow (runs migrations on deployment server):
```yaml
# ✅ This works because deployment server can reach database  
- name: Run migrations on deployment server
  env:
    SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
  run: |
    sshpass -e ssh ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH'
    cd /home/django/ProjectMeats/backend
    source venv/bin/activate
    python manage.py migrate --noinput
    SSH
```

---

## Recommended Configuration by Environment

### Development Environment:
- **Option 1**: Add specific GitHub IP ranges (see script below)
- **Fallback**: Temporarily allow 0.0.0.0/0 with strong password

### UAT Environment:
- **Option 2**: Use SSH tunnel through deployment server
- Keep database restricted to deployment server IP only

### Production Environment:
- **Option 2**: Use SSH tunnel through deployment server (REQUIRED)
- **Never** open production database to GitHub Actions

---

## Script to Fetch GitHub Actions IP Ranges

Save this as `scripts/get-github-actions-ips.sh`:

```bash
#!/bin/bash
#
# Fetch current GitHub Actions IP ranges
# These need to be added to DigitalOcean database trusted sources
#

echo "Fetching GitHub Actions IP ranges..."
echo ""

# Fetch from GitHub API
RESPONSE=$(curl -s https://api.github.com/meta)

# Extract actions IP ranges
ACTIONS_IPS=$(echo "$RESPONSE" | jq -r '.actions[]' 2>/dev/null)

if [ -z "$ACTIONS_IPS" ]; then
    echo "Error: Could not fetch IP ranges from GitHub API"
    exit 1
fi

echo "GitHub Actions IP Ranges (for Actions runners):"
echo "================================================"
echo "$ACTIONS_IPS"
echo ""
echo "Total ranges: $(echo "$ACTIONS_IPS" | wc -l)"
echo ""
echo "To add these to DigitalOcean:"
echo "1. Go to https://cloud.digitalocean.com/databases"
echo "2. Select your database"
echo "3. Go to Settings → Trusted Sources"
echo "4. Add each IP range above"
echo ""
echo "Note: These ranges may change over time."
echo "Monitor GitHub's meta API for updates."
```

**Usage:**
```bash
chmod +x scripts/get-github-actions-ips.sh
./scripts/get-github-actions-ips.sh
```

---

## Step-by-Step: Add IPs to DigitalOcean

### 1. Get GitHub Actions IPs

```bash
curl -s https://api.github.com/meta | jq -r '.actions[]'
```

**Example Output:**
```
13.64.0.0/16
13.65.0.0/16
13.68.0.0/16
... (many more)
```

### 2. Add to DigitalOcean Database

For **each IP range** from the list:

1. Go to: https://cloud.digitalocean.com/databases
2. Click your database cluster
3. Click "Settings" tab
4. Scroll to "Trusted Sources"
5. Click "Edit"
6. Click "Add trusted source"
7. Select "CIDR Block"
8. Enter the IP range (e.g., `13.64.0.0/16`)
9. Add description: `GitHub Actions - Range 1`
10. Click "Save"
11. **Repeat for each range** (there are typically 20-30 ranges)

### 3. Verify Connection

Trigger a deployment and check if migrations succeed:

```bash
gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)" --ref development
gh run watch
```

---

## Alternative: Use GitHub-Hosted Larger Runners with Static IPs

GitHub offers **larger runners with static IP addresses** for Enterprise customers:
- https://docs.github.com/en/actions/using-github-hosted-runners/about-larger-runners

**Requirements:**
- GitHub Enterprise Cloud or Enterprise Server
- Additional cost per runner
- Static IP addresses that can be allowlisted

---

## Monitoring and Maintenance

### Monitor Database Connections

```bash
# Check recent connections in DigitalOcean console
# Navigate to: Database → Metrics → Connections
```

### Update IP Ranges Regularly

GitHub Actions IP ranges change over time. Set up a monthly review:

```bash
# Create a cron job or GitHub Action to check for changes
curl -s https://api.github.com/meta | jq '.actions' > current-ranges.json
diff current-ranges.json previous-ranges.json
```

### Security Best Practices

1. **Use strong database passwords** (minimum 32 characters)
2. **Enable SSL/TLS** connections (required by DigitalOcean)
3. **Monitor connection logs** for suspicious activity
4. **Rotate passwords quarterly**
5. **Use read-only users** for non-migration workflows
6. **Limit database access** to specific IPs when possible

---

## Recommended Implementation Plan

### Phase 1: Development (Immediate)
1. Fetch GitHub Actions IP ranges
2. Add top 10 most common ranges to dev database
3. Test deployment workflow
4. Add remaining ranges if needed

### Phase 2: UAT (Next)
1. Implement SSH tunnel approach (see Option 2)
2. Remove GitHub Actions IPs from UAT database
3. Test deployment through SSH tunnel

### Phase 3: Production (Before Launch)
1. Use SSH tunnel approach only (see Option 2)
2. Ensure production database only allows deployment server IP
3. Document emergency access procedures

---

## Complete Example: SSH Tunnel Approach

Here's how to update the workflow to use SSH tunnel:

```yaml
migrate:
  runs-on: ubuntu-latest
  needs: [build-and-push, test-backend]
  environment: dev-backend
  timeout-minutes: 15
  
  steps:
    - name: Setup SSH
      run: |
        sudo apt-get update
        sudo apt-get install -y sshpass
        mkdir -p ~/.ssh
        ssh-keyscan -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts
    
    - name: Run migrations via SSH on deployment server
      env:
        SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
      run: |
        sshpass -e ssh -o StrictHostKeyChecking=yes \
          ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH_END'
        set -euo pipefail
        
        cd /home/django/ProjectMeats/backend
        
        # Activate virtual environment if exists
        if [ -f "venv/bin/activate" ]; then
          source venv/bin/activate
        fi
        
        # Run migrations
        python manage.py migrate --fake-initial --noinput
        
        echo "✓ Migrations completed successfully"
        SSH_END
```

**Advantages:**
- ✅ No need to modify database firewall
- ✅ More secure (database only accessible from deployment server)
- ✅ Works for all environments
- ✅ No maintenance of IP ranges needed

**Disadvantages:**
- ⚠️ Requires deployment server to be running
- ⚠️ Migrations run after container is built (not before)

---

## Quick Decision Matrix

| Scenario | Recommended Solution |
|----------|---------------------|
| Development database, fast testing | Option 1: Add GitHub IPs (temporary) |
| UAT database | Option 2: SSH tunnel |
| Production database | Option 2: SSH tunnel (REQUIRED) |
| Need to test migrations before build | Option 1: Add GitHub IPs |
| Security-first approach | Option 2: SSH tunnel |

---

## Next Steps

1. **Choose your approach** based on the decision matrix above
2. **For Option 1**: Run `./scripts/get-github-actions-ips.sh` and add IPs to DigitalOcean
3. **For Option 2**: I'll help update the workflows to use SSH tunnel
4. **Test** the deployment workflow
5. **Monitor** the migrate job logs for successful connection

---

## Additional Resources

- [GitHub Actions IP Ranges](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#ip-addresses)
- [GitHub Meta API](https://api.github.com/meta)
- [DigitalOcean Database Firewall](https://docs.digitalocean.com/products/databases/postgresql/how-to/secure/)
- [SSH Tunneling Guide](https://www.ssh.com/academy/ssh/tunneling-example)

---

## Support

If you need help implementing either solution, let me know which option you prefer and I can provide specific step-by-step instructions or update the workflows accordingly.
