#!/bin/bash
# ProjectMeats Development Server Stop Script
# This script gracefully stops both backend and frontend servers
# Usage: ./stop_dev.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ProjectMeats Development Server Stop    ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo ""

# Stop by PID files first
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}→${NC} Stopping backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
        sleep 1
        kill -9 "$BACKEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Backend stopped"
    fi
    rm "$LOG_DIR/backend.pid"
fi

if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}→${NC} Stopping frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
        sleep 1
        kill -9 "$FRONTEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Frontend stopped"
    fi
    rm "$LOG_DIR/frontend.pid"
fi

# Kill any remaining processes
echo -e "${YELLOW}→${NC} Cleaning up any remaining processes..."
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "react-app-rewired" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
sleep 1

echo ""
echo -e "${GREEN}✓ All development servers stopped${NC}"
echo ""
