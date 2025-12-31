#!/bin/bash
#
# Setup Database Secrets for GitHub Actions
#
# This script helps you configure database connection secrets for deployment workflows.
# It will prompt you for the DATABASE_URL for each environment and set the secrets.
#
# Usage:
#   ./scripts/setup-db-secrets.sh
#
# Prerequisites:
#   - GitHub CLI (gh) installed and authenticated
#   - Repository admin or secrets management permissions
#

set -e

echo "======================================"
echo "Database Secrets Configuration Setup"
echo "======================================"
echo ""
echo "This script will help you configure DATABASE_URL secrets for deployment workflows."
echo ""
echo "DATABASE_URL Format:"
echo "  postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME"
echo ""
echo "Example for DigitalOcean:"
echo "  postgresql://doadmin:RANDOM_PWD@db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com:25060/defaultdb"
echo ""
echo "======================================"
echo ""

# Function to validate DATABASE_URL format
validate_db_url() {
    local url="$1"
    if [[ ! "$url" =~ ^postgresql:// ]]; then
        echo "Error: URL must start with 'postgresql://'"
        return 1
    fi
    if [[ ! "$url" =~ ^postgresql://[^:]+:[^@]+@[^:]+:[0-9]+/ ]]; then
        echo "Error: Invalid format. Expected: postgresql://user:password@host:port/database"
        return 1
    fi
    return 0
}

# Function to set secret for an environment
set_environment_secret() {
    local env_name="$1"
    local secret_name="$2"
    local secret_value="$3"
    
    echo "Setting $secret_name for environment: $env_name..."
    
    if gh secret set "$secret_name" --env "$env_name" --body "$secret_value"; then
        echo "✓ Successfully set $secret_name for $env_name"
        return 0
    else
        echo "✗ Failed to set $secret_name for $env_name"
        return 1
    fi
}

# Function to configure an environment
configure_environment() {
    local env_name="$1"
    local secret_name="$2"
    local display_name="$3"
    
    echo ""
    echo "======================================"
    echo "Configuring: $display_name"
    echo "Environment: $env_name"
    echo "Secret Name: $secret_name"
    echo "======================================"
    echo ""
    
    # Check if user wants to configure this environment
    read -p "Do you want to configure $display_name? (y/n): " configure
    if [[ "$configure" != "y" && "$configure" != "Y" ]]; then
        echo "Skipping $display_name..."
        return 0
    fi
    
    # Prompt for DATABASE_URL
    echo ""
    echo "Enter the DATABASE_URL for $display_name"
    echo "(Leave empty to skip, or paste your connection string):"
    read -s -p "DATABASE_URL: " db_url
    echo ""
    
    # Skip if empty
    if [[ -z "$db_url" ]]; then
        echo "No URL provided, skipping..."
        return 0
    fi
    
    # Validate format
    if ! validate_db_url "$db_url"; then
        echo "Invalid DATABASE_URL format. Skipping $display_name..."
        return 1
    fi
    
    # Parse and display components (without password)
    local db_user=$(echo "$db_url" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
    local db_host=$(echo "$db_url" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    local db_port=$(echo "$db_url" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    local db_name=$(echo "$db_url" | sed -n 's|.*/\([^?]*\).*|\1|p')
    
    echo ""
    echo "Parsed credentials:"
    echo "  User: $db_user"
    echo "  Host: $db_host"
    echo "  Port: $db_port"
    echo "  Database: $db_name"
    echo "  Password: ***hidden***"
    echo ""
    
    read -p "Does this look correct? (y/n): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled. Please try again with the correct URL."
        return 1
    fi
    
    # Set the secret
    if set_environment_secret "$env_name" "$secret_name" "$db_url"; then
        echo ""
        echo "✓ Successfully configured $display_name!"
        return 0
    else
        echo ""
        echo "✗ Failed to configure $display_name"
        return 1
    fi
}

# Main execution
echo "Starting configuration..."
echo ""

# Configure Development Environment
configure_environment "dev-backend" "DEV_DB_URL" "Development Environment"

# Configure UAT Environment
configure_environment "uat2-backend" "UAT_DB_URL" "UAT Environment"

# Configure Production Environment
configure_environment "prod2-backend" "PROD_DB_URL" "Production Environment"

echo ""
echo "======================================"
echo "Configuration Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Trigger a deployment workflow to test the configuration"
echo "2. Monitor the 'migrate' job logs to verify database connection"
echo "3. Check for successful migration output"
echo ""
echo "To trigger development deployment:"
echo "  gh workflow run \"Deploy Dev (Frontend + Backend via DOCR and GHCR)\" --ref development"
echo ""
echo "To monitor workflow:"
echo "  gh run watch"
echo ""
echo "For more information, see: DEPLOYMENT_DB_SECRETS_SETUP.md"
echo ""
