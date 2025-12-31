#!/usr/bin/env bash
#
# Pre-commit hook: Lint Docker port bindings
# 
# Purpose: Prevent binding to privileged ports (< 1024) in Docker containers
#          to avoid "address already in use" errors in CI/CD deployments.
#
# Context: We experienced failures when `docker run -p 80:80` tried to bind
#          to port 80, which was already occupied by host services (nginx).
#
# Solution: This hook enforces using high ports (>= 1024) for containers,
#           with traffic routed via a reverse proxy (nginx/traefik).
#
# Usage: Run automatically via pre-commit, or manually:
#        ./scripts/lint-docker-ports.sh
#
# Exit codes:
#   0 = No issues found
#   1 = Privileged port binding detected

set -euo pipefail

# Color output for better readability
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}Docker Port Binding Linter${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo ""

# Function to check if a port is privileged
is_privileged_port() {
    local port=$1
    if [[ $port -lt 1024 ]]; then
        return 0  # True - is privileged
    fi
    return 1  # False - not privileged
}

# Function to check if line has explicit exception comment
has_exception_comment() {
    local line=$1
    # Check for exception markers: # allowed-proxy, # allowed-privileged, # allow:80
    if echo "$line" | grep -qE '#\s*(allowed?-proxy|allowed?-privileged|allow:\d+)'; then
        return 0  # True - has exception
    fi
    return 1  # False - no exception
}

# Function to extract host port from binding
extract_host_port() {
    local binding=$1
    # Remove quotes and whitespace
    binding=$(echo "$binding" | tr -d '"' | tr -d "'" | xargs)
    
    # Extract host port (first number before colon, or between IP and colon)
    if echo "$binding" | grep -qE '^\d+\.\d+\.\d+\.\d+:\d+'; then
        # Format: IP:HOST_PORT:CONTAINER_PORT
        echo "$binding" | sed -E 's/^[^:]+:([0-9]+).*/\1/'
    elif echo "$binding" | grep -qE '^\d+:'; then
        # Format: HOST_PORT:CONTAINER_PORT
        echo "$binding" | sed -E 's/^([0-9]+).*/\1/'
    else
        echo ""
    fi
}

# Function to check a single file
check_file() {
    local file=$1
    local file_errors=0
    
    echo -e "${BLUE}Checking:${NC} $file"
    
    # Read entire file content
    local content=$(cat "$file")
    local line_num=0
    
    while IFS= read -r line; do
        ((line_num++))
        
        # Skip empty lines and full-line comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Check for -p flag with port binding (look for standalone -p lines)
        if echo "$line" | grep -qE -- '^\s+-p\s+[0-9]+:[0-9]+'; then
            # Extract port binding, remove backslash and whitespace
            binding=$(echo "$line" | sed -E 's/^\s+-p\s+//' | sed 's/\s*\\$//' | xargs)
            host_port=$(echo "$binding" | sed -E 's/^([0-9]+).*/\1/')
            
            if [[ -n "$host_port" ]] && is_privileged_port "$host_port"; then
                if has_exception_comment "$line"; then
                    echo -e "  ${YELLOW}Line $line_num:${NC} Port $host_port binding found but ${GREEN}ALLOWED${NC} (exception comment)"
                    ((WARNINGS++))
                else
                    echo -e "  ${RED}✗ Line $line_num:${NC} Privileged port binding detected: ${RED}-p $binding${NC}"
                    echo -e "    ${YELLOW}Port $host_port is privileged (< 1024)${NC}"
                    echo -e "    ${GREEN}Fix:${NC} Use high port (e.g., -p 8080:80) and route via reverse proxy"
                    ((ERRORS++))
                    ((file_errors++))
                fi
            fi
        fi
        
        # Check for inline -p in docker run command
        if echo "$line" | grep -qE 'docker\s+run.*-p\s+[0-9]+:[0-9]+'; then
            while IFS= read -r binding; do
                [[ -z "$binding" ]] && continue
                host_port=$(echo "$binding" | sed -E 's/^([0-9]+).*/\1/')
                
                if [[ -n "$host_port" ]] && is_privileged_port "$host_port"; then
                    if has_exception_comment "$line"; then
                        echo -e "  ${YELLOW}Line $line_num:${NC} Port $host_port binding found but ${GREEN}ALLOWED${NC} (exception comment)"
                        ((WARNINGS++))
                    else
                        echo -e "  ${RED}✗ Line $line_num:${NC} Privileged port binding detected: ${RED}-p $binding${NC}"
                        echo -e "    ${YELLOW}Port $host_port is privileged (< 1024)${NC}"
                        echo -e "    ${GREEN}Fix:${NC} Use high port (e.g., -p 8080:80) and route via reverse proxy"
                        ((ERRORS++))
                        ((file_errors++))
                    fi
                fi
            done < <(echo "$line" | grep -oE -- '-p\s+[0-9]+:[0-9]+' | sed 's/-p\s*//')
        fi
        
        # Check for docker-compose ports format: - "80:80"
        if echo "$line" | grep -qE '^\s*-\s*["\x27]?[0-9]+:[0-9]+'; then
            binding=$(echo "$line" | sed -E 's/^\s*-\s*//' | tr -d '"' | tr -d "'" | sed 's/#.*//' | xargs)
            host_port=$(extract_host_port "$binding")
            
            if [[ -n "$host_port" ]] && is_privileged_port "$host_port"; then
                if has_exception_comment "$line"; then
                    echo -e "  ${YELLOW}Line $line_num:${NC} Port $host_port binding found but ${GREEN}ALLOWED${NC} (exception comment)"
                    ((WARNINGS++))
                else
                    echo -e "  ${RED}✗ Line $line_num:${NC} Privileged port binding detected: ${RED}$binding${NC}"
                    echo -e "    ${YELLOW}Port $host_port is privileged (< 1024)${NC}"
                    echo -e "    ${GREEN}Fix:${NC} Use high port (e.g., \"8080:80\") and route via reverse proxy"
                    ((ERRORS++))
                    ((file_errors++))
                fi
            fi
        fi
        
    done <<< "$content"
    
    if [[ $file_errors -eq 0 ]]; then
        echo -e "  ${GREEN}✓ No privileged port bindings found${NC}"
    fi
    echo ""
    
    return $file_errors
}

# Main execution
echo "Scanning for privileged port bindings in workflows..."
echo ""

# Find all workflow files and docker-compose files
FILES_TO_CHECK=(
    $(find .github/workflows -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null || true)
    $(find . -maxdepth 3 -type f \( -name "docker-compose*.yml" -o -name "docker-compose*.yaml" \) 2>/dev/null || true)
)

if [[ ${#FILES_TO_CHECK[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No workflow or docker-compose files found to check${NC}"
    exit 0
fi

# Check each file
for file in "${FILES_TO_CHECK[@]}"; do
    if [[ -f "$file" ]]; then
        check_file "$file" || true  # Don't exit on individual file errors
    fi
done

# Summary
echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}==================================================================${NC}"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ No errors found!${NC}"
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}  $WARNINGS warning(s) - exceptions allowed by comments${NC}"
    fi
    echo ""
    echo -e "${GREEN}All Docker port bindings follow best practices.${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}  $WARNINGS warning(s) - exceptions allowed by comments${NC}"
    fi
    echo ""
    echo -e "${RED}Please fix the privileged port bindings above.${NC}"
    echo ""
    echo -e "${BLUE}Best Practices:${NC}"
    echo "  1. Use high ports (>= 1024) for container host bindings"
    echo "     Example: -p 8080:80 instead of -p 80:80"
    echo ""
    echo "  2. Route external traffic via reverse proxy (nginx/traefik)"
    echo "     - Proxy listens on privileged ports (80, 443)"
    echo "     - Forwards to container on high port"
    echo ""
    echo "  3. If privileged port binding is intentional, add exception comment:"
    echo "     -p 80:80  # allowed-proxy - nginx reverse proxy"
    echo ""
    echo "  4. Or use sudo fuser -k to free the port before binding:"
    echo "     sudo fuser -k 80/tcp || true  # Free port 80"
    echo "     docker run -p 80:80 ...       # Now safe to bind"
    echo ""
    echo -e "${BLUE}Why this matters:${NC}"
    echo "  - Privileged ports require root or specific capabilities"
    echo "  - Host services (nginx, systemd) often bind to 80/443"
    echo "  - Conflicts cause 'address already in use' deployment failures"
    echo "  - High ports avoid conflicts and follow principle of least privilege"
    echo ""
    exit 1
fi
