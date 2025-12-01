# 🚀 Development Setup Guide

**Complete guide to set up your local development environment for ProjectMeats**

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads/)

Verify installations:
```bash
python --version  # Should show 3.9 or higher
node --version    # Should show 16 or higher
npm --version     # Should show 7 or higher
psql --version    # Should show 12 or higher
git --version     # Should show 2.x or higher
```

## Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats

# Run the automated startup script
./start_dev.sh
```

The `start_dev.sh` script will automatically:
- ✅ Start PostgreSQL service
- ✅ Create database and user
- ✅ Install Python dependencies
- ✅ Install Node dependencies
- ✅ Run database migrations
- ✅ Start backend server (port 8000)
- ✅ Start frontend server (port 3000)

**Your application will be running at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin

To stop the servers:
```bash
./stop_dev.sh
```

### Option 2: Manual Setup

If you prefer manual control or need to troubleshoot:

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats
```

#### Step 2: Set Up PostgreSQL

Start PostgreSQL and create the database:

**Ubuntu/Debian:**
```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE projectmeats_dev;"
sudo -u postgres psql -c "CREATE USER projectmeats_dev WITH PASSWORD 'devpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"
sudo -u postgres psql -c "ALTER DATABASE projectmeats_dev OWNER TO projectmeats_dev;"
```

**macOS:**
```bash
brew services start postgresql
createdb projectmeats_dev
createuser -P projectmeats_dev  # Enter password: devpassword
psql -d projectmeats_dev -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"
```

**Windows:**
```powershell
# Start PostgreSQL service from Services panel or:
net start postgresql-x64-16  # Adjust version number as needed

# Then use psql or pgAdmin to create database and user
```

#### Step 3: Set Up Backend

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Update backend/.env to use PostgreSQL
# DATABASE_URL=postgresql://projectmeats_dev:devpassword@localhost:5432/projectmeats_dev

# Install Python dependencies
pip install -r backend/requirements.txt

# Run migrations
cd backend
python manage.py migrate
cd ..
```

#### Step 4: Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

#### Step 5: Set Up Pre-commit Hooks (REQUIRED)

**⚠️ CRITICAL**: This step is mandatory to prevent CI failures:

```bash
pre-commit install
```

This installs Git hooks that:
- Format code automatically
- Validate Django migrations
- Check for syntax errors
- Prevent large file commits

#### Step 6: Start Development Servers

**Option A: Start Both Servers with Make**
```bash
make dev
```

**Option B: Start Servers in Separate Terminals**

Terminal 1 (Backend):
```bash
cd backend
python manage.py runserver
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

## Environment Configuration

### Backend Environment (.env)

The backend uses a `.env` file located at `backend/.env`. Copy from `backend/.env.example` and update as needed:

```env
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
DJANGO_SETTINGS_MODULE=projectmeats.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://projectmeats_dev:devpassword@localhost:5432/projectmeats_dev

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# API Configuration
API_VERSION=v1

# Email (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
```

### Frontend Environment (.env)

The frontend uses environment variables too. Create `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

## Creating a Superuser

To access the Django admin panel, create a superuser:

```bash
cd backend
python manage.py createsuperuser
```

Or use the automated command:

```bash
make superuser
```

## Common Development Tasks

### Database Operations

```bash
# Create new migrations
make migrations

# Apply migrations
make migrate

# Open Django shell
make shell

# Reset database (⚠️ Development only - will lose all data)
cd backend
rm db.sqlite3  # If using SQLite
python manage.py flush  # If using PostgreSQL
python manage.py migrate
```

### Running Tests

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# Specific test file
cd backend
python manage.py test apps.suppliers.tests.test_models
```

### Code Quality

```bash
# Format code (black, isort)
make format

# Lint code (flake8)
make lint

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Development Server Management

```bash
# Start all servers (automated)
./start_dev.sh
# or
make start

# Stop all servers
./stop_dev.sh
# or
make stop

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

## Troubleshooting

### PostgreSQL Connection Issues

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Check if PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list  # macOS
   ```

2. Start PostgreSQL if not running:
   ```bash
   sudo systemctl start postgresql  # Linux
   brew services start postgresql  # macOS
   ```

3. Verify database exists:
   ```bash
   psql -U projectmeats_dev -d projectmeats_dev -h localhost
   ```

### Port Already in Use

**Error**: `Error: That port is already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>

# Or use the automated script
./stop_dev.sh
./start_dev.sh
```

### Migration Errors

**Error**: `django.db.utils.OperationalError: near "(": syntax error`

This means you're using SQLite but migrations require PostgreSQL. Update your `backend/.env`:

```env
DATABASE_URL=postgresql://projectmeats_dev:devpassword@localhost:5432/projectmeats_dev
```

### Frontend Build Errors

**Error**: `Module not found` or compilation errors

**Solutions**:
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear npm cache if needed
npm cache clean --force
npm install
```

### Pre-commit Hook Failures

**Error**: Pre-commit hooks failing on commit

**Solution**:
```bash
# Run hooks manually to see errors
pre-commit run --all-files

# Format code
make format

# Re-run hooks
pre-commit run --all-files

# If migrations check fails, create migrations
cd backend
python manage.py makemigrations
```

## Development Workflow

### Branch Naming

Use the following branch naming conventions:

```
feature/<description>     # New features
fix/<description>         # Bug fixes
chore/<description>       # Maintenance tasks
docs/<description>        # Documentation updates
refactor/<description>    # Code refactoring
test/<description>        # Test improvements
```

### Making Changes

1. Create a new branch from `development`:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/my-new-feature
   ```

2. Make your changes and test thoroughly

3. Run code quality checks:
   ```bash
   make format
   make lint
   make test
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. Push to GitHub:
   ```bash
   git push origin feature/my-new-feature
   ```

6. Create a Pull Request to `development` branch

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- GitLens
- Django

Workspace settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Open project in PyCharm
2. Set Python interpreter to your virtual environment
3. Configure Django support:
   - Settings → Languages & Frameworks → Django
   - Enable Django support
   - Django project root: `/path/to/backend`
   - Settings: `projectmeats/settings/development.py`
4. Configure code style to use Black

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Next Steps

Once your development environment is set up:

1. **Explore the codebase**: Start with the README.md
2. **Read the documentation**: Check the `docs/` directory
3. **Run the tests**: Ensure everything is working
4. **Try the API**: Visit http://localhost:8000/api/docs/
5. **Make a change**: Create a branch and implement a small feature
6. **Submit a PR**: Follow the contribution guidelines

## Additional Resources

- **[README.md](README.md)** - Project overview and quick start
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md)** - Backend architecture
- **[docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md)** - Frontend architecture
- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Deployment guide
- **[branch-workflow-checklist.md](branch-workflow-checklist.md)** - Branch workflow

## Getting Help

- **Documentation**: Browse the `docs/` directory
- **Issues**: Check [GitHub Issues](https://github.com/Meats-Central/ProjectMeats/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/Meats-Central/ProjectMeats/discussions)

---

**Happy Coding! 🎉**
