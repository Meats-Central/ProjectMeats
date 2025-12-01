#!/bin/bash
# Deployment Rollback Script
# Rolls back to previous deployment version

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT="${1:-}"
COMPONENT="${2:-all}"  # frontend, backend, or all

if [ -z "$ENVIRONMENT" ]; then
    echo -e "${RED}Error: Environment not specified${NC}"
    echo "Usage: $0 <dev|uat|prod> [frontend|backend|all]"
    exit 1
fi

echo "=== Deployment Rollback: $ENVIRONMENT ($COMPONENT) ==="

# Function to get previous image tag
get_previous_tag() {
    local image=$1
    # List images and get the second most recent (first is current)
    docker images --format "{{.Tag}}" "$image" | grep -E "^${ENVIRONMENT}-" | head -n 2 | tail -n 1
}

# Function to rollback container
rollback_container() {
    local container_name=$1
    local image=$2
    local port_mapping=$3
    local volumes=$4
    local env_file=${5:-}
    
    echo -e "\n${YELLOW}Rolling back $container_name...${NC}"
    
    # Get previous tag
    local prev_tag=$(get_previous_tag "$image")
    if [ -z "$prev_tag" ]; then
        echo -e "${RED}✗ No previous version found for rollback${NC}"
        return 1
    fi
    
    echo "Previous version: $prev_tag"
    
    # Stop current container
    echo "Stopping current container..."
    docker stop "$container_name" >/dev/null 2>&1 || true
    docker rm "$container_name" >/dev/null 2>&1 || true
    
    # Start container with previous version
    echo "Starting container with previous version..."
    local docker_cmd="docker run -d --name $container_name --restart unless-stopped $port_mapping"
    
    if [ -n "$env_file" ]; then
        docker_cmd="$docker_cmd --env-file $env_file"
    fi
    
    if [ -n "$volumes" ]; then
        docker_cmd="$docker_cmd $volumes"
    fi
    
    docker_cmd="$docker_cmd $image:$prev_tag"
    
    if eval "$docker_cmd"; then
        echo -e "${GREEN}✓ Rollback successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Rollback failed${NC}"
        return 1
    fi
}

# Rollback frontend
rollback_frontend() {
    echo -e "\n${YELLOW}=== Rolling back frontend ===${NC}"
    local image="$REGISTRY/$FRONTEND_IMAGE"
    local volumes="-v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro"
    
    rollback_container "pm-frontend" "$image" "-p 8080:80" "$volumes"
}

# Rollback backend
rollback_backend() {
    echo -e "\n${YELLOW}=== Rolling back backend ===${NC}"
    local image="$REGISTRY/$BACKEND_IMAGE"
    local env_file="/home/django/ProjectMeats/backend/.env"
    local volumes="-v /home/django/ProjectMeats/media:/app/media -v /home/django/ProjectMeats/staticfiles:/app/staticfiles"
    
    rollback_container "pm-backend" "$image" "-p 8000:8000" "$volumes" "$env_file"
}

# Create rollback snapshot
create_snapshot() {
    echo -e "\n${YELLOW}Creating rollback snapshot...${NC}"
    local snapshot_file="/tmp/pm-rollback-snapshot-$(date +%Y%m%d-%H%M%S).json"
    
    docker ps --format json | jq -s '.' > "$snapshot_file"
    echo -e "${GREEN}✓ Snapshot saved: $snapshot_file${NC}"
}

# Verify rollback
verify_rollback() {
    echo -e "\n${YELLOW}Verifying rollback...${NC}"
    local failed=0
    
    if [ "$COMPONENT" = "frontend" ] || [ "$COMPONENT" = "all" ]; then
        if ! docker ps | grep -q pm-frontend; then
            echo -e "${RED}✗ Frontend container not running${NC}"
            failed=1
        else
            echo -e "${GREEN}✓ Frontend container running${NC}"
        fi
    fi
    
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        if ! docker ps | grep -q pm-backend; then
            echo -e "${RED}✗ Backend container not running${NC}"
            failed=1
        else
            echo -e "${GREEN}✓ Backend container running${NC}"
        fi
    fi
    
    return $failed
}

# Main rollback process
main() {
    # Create snapshot before rollback
    create_snapshot
    
    case "$COMPONENT" in
        frontend)
            rollback_frontend
            ;;
        backend)
            rollback_backend
            ;;
        all)
            rollback_backend
            rollback_frontend
            ;;
        *)
            echo -e "${RED}Invalid component: $COMPONENT${NC}"
            exit 1
            ;;
    esac
    
    # Verify rollback
    if verify_rollback; then
        echo -e "\n${GREEN}=== Rollback completed successfully ===${NC}"
        return 0
    else
        echo -e "\n${RED}=== Rollback verification failed ===${NC}"
        return 1
    fi
}

main
