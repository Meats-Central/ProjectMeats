# ProjectMeats Development Makefile
# Provides essential development commands for Django + React application

.PHONY: help setup dev start stop test clean docs format lint env-dev env-staging env-prod env-validate env-secrets deploy-test deploy-check health-check deploy-simulate

# Default target
help:
	@echo "ProjectMeats Development Commands"
	@echo ""
	@echo "Quick Start:"
	@echo "  ./start_dev.sh  - Start all servers (PostgreSQL + Django + React)"
	@echo "  ./stop_dev.sh   - Stop all running servers"
	@echo "  make dev        - Start development servers (manual)"
	@echo ""
	@echo "Development:"
	@echo "  make start      - Start servers with PostgreSQL (uses start_dev.sh)"
	@echo "  make stop       - Stop all servers (uses stop_dev.sh)"
	@echo "  make backend    - Start Django server only"
	@echo "  make frontend   - Start React server only"
	@echo "  make migrate    - Apply database migrations"
	@echo "  make migrations - Create new migrations"
	@echo "  make shell      - Open Django shell"
	@echo "  make validate-db-config - Validate database environment variables"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate    - Apply database migrations"
	@echo "  make migrations - Create new migrations"
	@echo "  make shell      - Open Django shell"
	@echo "  make superuser  - Create/update superuser and root tenant"
	@echo "  make sync-superuser - Sync superuser password from environment"
	@echo "  make setup-superuser - Alias for sync-superuser"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test       - Run all tests (backend + frontend)"
	@echo "  make test-backend  - Run Django tests only"
	@echo "  make test-frontend - Run React tests only"
	@echo "  make format     - Format code (black, isort)"
	@echo "  make lint       - Lint code (flake8)"
	@echo "  make docs       - Generate API documentation"
	@echo "  make clean      - Clean build artifacts"
	@echo ""
	@echo "Environment Management:"
	@echo "  make env-dev      - Set up development environment"  
	@echo "  make env-staging  - Set up staging environment"
	@echo "  make env-prod     - Set up production environment"
	@echo "  make env-validate - Validate environment configuration"
	@echo "  make env-secrets  - Generate secure secrets"
	@echo ""
	@echo "Deployment & Testing:"
	@echo "  make deploy-test    - Test deployment configuration"
	@echo "  make deploy-check   - Comprehensive deployment validation" 
	@echo "  make deploy-simulate- Simulate full deployment process"
	@echo "  make health-check   - Check live application health (requires URL)"
	@echo ""
	@echo "See README.md for complete documentation."

# Setup commands
setup: setup-backend setup-frontend
	@echo "✅ Complete setup finished! Run 'make dev' to start development."

setup-backend:
	@echo "🔧 Setting up Django backend..."
	cd backend && cp -n .env.example .env 2>/dev/null || true
	cd backend && pip install -r requirements.txt
	cd backend && python manage.py migrate
	@echo "✅ Backend setup complete!"

setup-frontend:
	@echo "🔧 Setting up React frontend..."
	cd frontend && npm install
	@echo "✅ Frontend setup complete!"

# Development commands
start:
	@echo "🚀 Starting all development servers (PostgreSQL + Backend + Frontend)..."
	@./start_dev.sh

stop:
	@echo "🛑 Stopping all development servers..."
	@./stop_dev.sh

dev: validate-db-config
	@echo "🚀 Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@make -j2 backend frontend

validate-db-config:
	@echo "🔍 Validating database configuration..."
	@if [ -z "$$DB_ENGINE" ]; then \
		echo "⚠️  DB_ENGINE not set, defaulting to PostgreSQL"; \
		echo "💡 Configure DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT in config/environments/development.env"; \
	elif [ "$$DB_ENGINE" = "django.db.backends.postgresql" ]; then \
		echo "✅ Using PostgreSQL"; \
		if [ -z "$$DB_NAME" ] || [ -z "$$DB_USER" ] || [ -z "$$DB_PASSWORD" ] || [ -z "$$DB_HOST" ]; then \
			echo "❌ PostgreSQL requires all connection variables:"; \
			[ -z "$$DB_NAME" ] && echo "   - DB_NAME is not set"; \
			[ -z "$$DB_USER" ] && echo "   - DB_USER is not set"; \
			[ -z "$$DB_PASSWORD" ] && echo "   - DB_PASSWORD is not set"; \
			[ -z "$$DB_HOST" ] && echo "   - DB_HOST is not set"; \
			echo "💡 Set these in config/environments/development.env or as environment variables"; \
			exit 1; \
		else \
			echo "✅ All PostgreSQL variables are set"; \
		fi \
	else \
		echo "❌ Invalid DB_ENGINE: $$DB_ENGINE"; \
		echo "   Only django.db.backends.postgresql is supported"; \
		exit 1; \
	fi

backend:
	@echo "🐍 Starting Django development server..."
	cd backend && python manage.py runserver

frontend:
	@echo "⚛️  Starting React development server..."
	cd frontend && npm start

# Database commands
migrate:
	cd backend && python manage.py migrate

migrations:
	cd backend && python manage.py makemigrations

shell:
	cd backend && python manage.py shell

superuser:
	@echo "👤 Creating superuser and root tenant..."
	cd backend && python manage.py create_super_tenant

sync-superuser:
	@echo "🔄 Syncing superuser password from environment..."
	cd backend && DJANGO_ENV=development python manage.py setup_superuser

# Alias for setup-superuser (for consistency with setup_superuser.py command)
setup-superuser: sync-superuser

# Testing commands
test: test-backend test-frontend

test-backend:
	@echo "🧪 Running Django tests..."
	cd backend && python manage.py test

test-frontend:
	@echo "🧪 Running React tests..."
	cd frontend && CI=true npm test -- --watchAll=false --passWithNoTests

# Code quality
format:
	@echo "🎨 Formatting code..."
	cd backend && black . --exclude=migrations
	cd backend && isort . --skip=migrations

lint:
	@echo "🔍 Linting code..."
	cd backend && flake8 . --exclude=migrations

# Documentation and cleanup
docs:
	@echo "📚 Generating API documentation..."
	cd backend && python manage.py spectacular --file ../docs/api_schema.yml
	@echo "✅ API schema generated at docs/api_schema.yml"

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf build node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Environment management commands
env-dev:
	@echo "🔧 Setting up development environment..."
	python config/manage_env.py setup development

env-staging:
	@echo "🔧 Setting up staging environment..."
	python config/manage_env.py setup staging

env-prod:
	@echo "🔧 Setting up production environment..."
	python config/manage_env.py setup production

env-validate:
	@echo "🔍 Validating environment configuration..."
	python config/manage_env.py validate

env-secrets:
	@echo "🔐 Generating secure secrets..."
	python config/manage_env.py generate-secrets

# Deployment testing commands
deploy-test:
	@echo "🧪 Testing deployment configuration..."
	python test_deployment.py --environment development --validate-only

deploy-check:
	@echo "🧪 Running comprehensive deployment validation..."
	python test_deployment.py --environment production

health-check:
	@echo "🏥 Running health check on live application..."
	@echo "Usage: make health-check URL=https://your-app.ondigitalocean.app"
	@if [ -z "$(URL)" ]; then \
		echo "❌ Please specify URL: make health-check URL=https://your-app.com"; \
	else \
		python health_check.py $(URL) --verbose; \
	fi

deploy-simulate:
	@echo "🎭 Simulating full deployment process..."
	python simulate_deployment.py --environment production --dry-run