# 🚀 Quick Start Guide - Local Development

This guide will get you up and running with the ProjectMeats application in under 5 minutes.

## Prerequisites

- **Python 3.9+** - `python --version`
- **Node.js 16+** - `node --version`
- **PostgreSQL 12+** - Required for environment parity

## Option 1: One-Command Start (Recommended)

```bash
./start_dev.sh
```

This script will automatically:
- ✅ Start PostgreSQL if not running
- ✅ Create database and user if needed
- ✅ Install Python dependencies
- ✅ Install Node dependencies
- ✅ Run database migrations
- ✅ Free ports 3000 and 8000 if occupied
- ✅ Start backend server on port 8000
- ✅ Start frontend server on port 3000

**That's it!** Your application will be running at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

### To Stop Servers

```bash
./stop_dev.sh
```

## Option 2: Using Make Commands

```bash
# Start all servers (uses start_dev.sh)
make start

# Stop all servers (uses stop_dev.sh)
make stop
```

## Option 3: Manual Setup

If you prefer manual control:

### 1. Start PostgreSQL

```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start if not running
sudo service postgresql start
```

### 2. Create Database

```bash
# Create database and user
sudo -u postgres psql -c "CREATE DATABASE projectmeats_dev;"
sudo -u postgres psql -c "CREATE USER projectmeats_dev WITH PASSWORD 'devpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"
sudo -u postgres psql -c "ALTER DATABASE projectmeats_dev OWNER TO projectmeats_dev;"
```

### 3. Install Dependencies

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 4. Run Migrations

```bash
cd backend && python manage.py migrate && cd ..
```

### 5. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend && python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm start
```

## Environment Configuration

The application uses PostgreSQL by default via `DATABASE_URL` in `backend/.env`:

```env
DATABASE_URL=postgresql://projectmeats_dev:devpassword@localhost:5432/projectmeats_dev
```

## Troubleshooting

### PostgreSQL Not Found

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

### Port Already in Use

The `start_dev.sh` script automatically handles this, but manually:

```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Kill process on port 3000
lsof -ti :3000 | xargs kill -9
```

### Database Connection Error

Check your `.env` file in the backend directory:

```bash
cat backend/.env | grep DATABASE_URL
```

Ensure PostgreSQL is running:

```bash
sudo service postgresql status
```

### Migration Errors

Reset migrations (⚠️ Development only - will lose data):

```bash
cd backend
rm db.sqlite3  # If using SQLite
python manage.py migrate --run-syncdb
```

### Frontend Won't Compile

Clear cache and reinstall:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## Viewing Logs

### Using start_dev.sh

Logs are automatically saved to the `logs/` directory:

```bash
# Watch backend logs
tail -f logs/backend.log

# Watch frontend logs
tail -f logs/frontend.log

# Watch both
tail -f logs/backend.log logs/frontend.log
```

### Check Server Status

```bash
# Check if servers are running
ps aux | grep -E "(runserver|npm start)" | grep -v grep

# Check ports
netstat -tuln | grep -E ":(3000|8000)"
# or
ss -tuln | grep -E ":(3000|8000)"
```

## Next Steps

Once your servers are running:

1. **Access the Application**: http://localhost:3000
2. **Create a Superuser**: `cd backend && python manage.py createsuperuser`
3. **Access Django Admin**: http://localhost:8000/admin
4. **API Documentation**: http://localhost:8000/api/schema/swagger-ui/

## Common Development Tasks

```bash
# Create database migrations
cd backend && python manage.py makemigrations

# Apply migrations
cd backend && python manage.py migrate

# Open Django shell
cd backend && python manage.py shell

# Run backend tests
cd backend && python manage.py test

# Run frontend tests
cd frontend && npm test

# Format code
make format

# Lint code
make lint
```

## Production Deployment

⚠️ **Never use `start_dev.sh` or `make start` in production!**

For production deployment, see:
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide
- [README.md](README.md) - Full documentation

## Getting Help

- **Documentation**: See `docs/` directory
- **Issues**: Check existing issues or create a new one
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy Coding! 🎉**
