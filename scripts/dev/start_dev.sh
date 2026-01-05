#!/bin/bash
# ProjectMeats Development Server Startup Script
# This script ensures PostgreSQL is running and starts both backend and frontend servers
# Usage: ./scripts/dev/start_dev.sh

set -e

# Get project root directory (two levels up from script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$LOG_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ProjectMeats Development Server Start   ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    if command_exists netstat; then
        netstat -tuln 2>/dev/null | grep -q ":$1 "
    elif command_exists ss; then
        ss -tuln 2>/dev/null | grep -q ":$1 "
    else
        lsof -i ":$1" >/dev/null 2>&1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    echo -e "${YELLOW}⚠️  Port $port is already in use. Attempting to free it...${NC}"
    
    if command_exists lsof; then
        lsof -ti ":$port" | xargs kill -9 2>/dev/null || true
    else
        fuser -k "$port/tcp" 2>/dev/null || true
    fi
    
    sleep 2
}

# Step 1: Check PostgreSQL
echo -e "${BLUE}[1/6]${NC} Checking PostgreSQL..."
if command_exists psql; then
    if sudo service postgresql status >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL is running"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting...${NC}"
        sudo service postgresql start
        sleep 2
        echo -e "${GREEN}✓${NC} PostgreSQL started"
    fi
    
    # Check/create database and user
    DB_NAME="${DB_NAME:-projectmeats_dev}"
    DB_USER="${DB_USER:-projectmeats_dev}"
    DB_PASSWORD="${DB_PASSWORD:-devpassword}"
    
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo -e "${GREEN}✓${NC} Database '$DB_NAME' exists"
    else
        echo -e "${YELLOW}⚠️  Creating database '$DB_NAME'...${NC}"
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
        sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Database created and configured"
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL not found. Please install PostgreSQL:"
    echo -e "  Ubuntu/Debian: ${YELLOW}sudo apt-get install postgresql${NC}"
    echo -e "  macOS: ${YELLOW}brew install postgresql${NC}"
    exit 1
fi

# Step 2: Check Python dependencies
echo -e "${BLUE}[2/6]${NC} Checking Python dependencies..."
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    if python -c "import django" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python dependencies installed"
    else
        echo -e "${YELLOW}⚠️  Installing Python dependencies...${NC}"
        pip install -r "$BACKEND_DIR/requirements.txt" -q
        echo -e "${GREEN}✓${NC} Dependencies installed"
    fi
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    exit 1
fi

# Step 3: Check Node dependencies
echo -e "${BLUE}[3/6]${NC} Checking Node dependencies..."
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node dependencies installed"
else
    echo -e "${YELLOW}⚠️  Installing Node dependencies...${NC}"
    cd "$FRONTEND_DIR" && npm install --silent
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Step 4: Run migrations
echo -e "${BLUE}[4/6]${NC} Running database migrations..."
cd "$BACKEND_DIR"
python manage.py migrate --no-input > "$LOG_DIR/migrations.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Migrations applied"
else
    echo -e "${RED}✗${NC} Migration failed. Check $LOG_DIR/migrations.log"
    cat "$LOG_DIR/migrations.log"
    exit 1
fi

# Step 5: Check and free ports
echo -e "${BLUE}[5/6]${NC} Checking ports..."
if port_in_use 8000; then
    kill_port 8000
fi
if port_in_use 3000; then
    kill_port 3000
fi
echo -e "${GREEN}✓${NC} Ports 8000 and 3000 are available"

# Step 6: Start servers
echo -e "${BLUE}[6/6]${NC} Starting development servers..."

# Kill any existing zombie processes
pkill -9 -f "manage.py runserver" 2>/dev/null || true
pkill -9 -f "react-app-rewired" 2>/dev/null || true
pkill -9 -f "npm.*start" 2>/dev/null || true
sleep 1

# Start backend
echo -e "${YELLOW}→${NC} Starting Django backend..."
cd "$BACKEND_DIR"
nohup python manage.py runserver 0.0.0.0:8000 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
sleep 3

# Verify backend started
if port_in_use 8000; then
    echo -e "${GREEN}✓${NC} Backend running on http://localhost:8000 (PID: $BACKEND_PID)"
else
    echo -e "${RED}✗${NC} Backend failed to start. Check $LOG_DIR/backend.log"
    tail -20 "$LOG_DIR/backend.log"
    exit 1
fi

# Start frontend
echo -e "${YELLOW}→${NC} Starting React frontend..."
cd "$FRONTEND_DIR"
nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${YELLOW}⏳${NC} Waiting for frontend to compile (this may take 15-30 seconds)..."

# Wait for frontend to be ready (check for "Compiled successfully" in logs)
for i in {1..30}; do
    if grep -q "Compiled successfully" "$LOG_DIR/frontend.log" 2>/dev/null; then
        break
    fi
    sleep 1
done

# Verify frontend started
if port_in_use 3000; then
    echo -e "${GREEN}✓${NC} Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"
else
    echo -e "${RED}✗${NC} Frontend failed to start. Check $LOG_DIR/frontend.log"
    tail -20 "$LOG_DIR/frontend.log"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🚀 Servers Running! 🚀            ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo ""
echo -e "  ${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "  ${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "  ${BLUE}Admin:${NC}    http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f $LOG_DIR/backend.log"
echo -e "  Frontend: tail -f $LOG_DIR/frontend.log"
echo ""
echo -e "${YELLOW}To stop servers:${NC}"
echo -e "  ./stop_dev.sh"
echo -e "  or: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop monitoring (servers will keep running)${NC}"
echo ""

# Save PIDs for stop script
echo "$BACKEND_PID" > "$LOG_DIR/backend.pid"
echo "$FRONTEND_PID" > "$LOG_DIR/frontend.pid"

# Monitor logs (optional - press Ctrl+C to detach)
trap "echo -e '\n${YELLOW}Servers are still running in background${NC}'; exit 0" INT
tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
