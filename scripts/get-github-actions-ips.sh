#!/bin/bash
#
# Fetch current GitHub Actions IP ranges
# These need to be added to DigitalOcean database trusted sources
#
# Usage: ./scripts/get-github-actions-ips.sh

set -e

echo "=================================================="
echo "GitHub Actions IP Ranges Fetcher"
echo "=================================================="
echo ""

# Check for required tools
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed"
    echo "Install with: sudo apt-get install jq"
    exit 1
fi

echo "Fetching IP ranges from GitHub API..."
echo ""

# Fetch from GitHub API
RESPONSE=$(curl -s https://api.github.com/meta)

if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch from GitHub API"
    exit 1
fi

# Extract actions IP ranges
ACTIONS_IPS=$(echo "$RESPONSE" | jq -r '.actions[]' 2>/dev/null)

if [ -z "$ACTIONS_IPS" ]; then
    echo "Error: Could not parse IP ranges from GitHub API response"
    exit 1
fi

# Count ranges
TOTAL_RANGES=$(echo "$ACTIONS_IPS" | wc -l)

echo "GitHub Actions IP Ranges (for Actions runners):"
echo "================================================"
echo ""
echo "$ACTIONS_IPS"
echo ""
echo "================================================"
echo "Total IP ranges found: $TOTAL_RANGES"
echo ""

# Save to file
OUTPUT_FILE="github-actions-ips-$(date +%Y%m%d).txt"
echo "$ACTIONS_IPS" > "$OUTPUT_FILE"
echo "✓ Saved to: $OUTPUT_FILE"
echo ""

# Instructions
echo "================================================"
echo "How to Add These to DigitalOcean:"
echo "================================================"
echo ""
echo "Option A: Add via Web Interface (Manual)"
echo "----------------------------------------"
echo "1. Go to https://cloud.digitalocean.com/databases"
echo "2. Select your database cluster"
echo "3. Go to Settings → Trusted Sources"
echo "4. Click 'Edit'"
echo "5. For each IP range above:"
echo "   - Click 'Add trusted source'"
echo "   - Select 'CIDR Block'"
echo "   - Paste the IP range (e.g., 13.64.0.0/16)"
echo "   - Add description: 'GitHub Actions - Range X'"
echo "   - Click 'Save'"
echo "6. Repeat for all $TOTAL_RANGES ranges"
echo ""
echo "Option B: Use DigitalOcean CLI (Automated)"
echo "-------------------------------------------"
echo "# Install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
echo "# Then run:"
echo ""
echo "DATABASE_ID=\"your-database-id\""
echo "while read -r ip; do"
echo "  doctl databases firewalls append \$DATABASE_ID --rule \"ip_addr:\$ip\""
echo "done < $OUTPUT_FILE"
echo ""
echo "================================================"
echo "Important Notes:"
echo "================================================"
echo ""
echo "⚠️  These IP ranges may change over time"
echo "⚠️  Monitor GitHub's meta API for updates"
echo "⚠️  Consider using SSH tunnel for production (see GITHUB_ACTIONS_DATABASE_ACCESS.md)"
echo "⚠️  This exposes your database to many IPs - use strong passwords"
echo ""
echo "Alternative: Use SSH tunnel instead (recommended for production)"
echo "See: GITHUB_ACTIONS_DATABASE_ACCESS.md"
echo ""
