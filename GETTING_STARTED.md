# Getting Started with ProjectMeats

## 🚀 Quick Setup (5 Minutes)

**Prerequisites**: Python 3.9+, Node.js 16+, PostgreSQL 12+

### Setup Commands
```bash
# Clone and setup environment
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats
python config/manage_env.py setup development

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
pre-commit install

# Run migrations and start servers
cd backend && python manage.py migrate && cd ..
./start_dev.sh
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/ (credentials in `config/environments/development.env`)

## 📝 Development Workflow

```bash
# Create feature branch
git checkout development && git pull
git checkout -b feature/your-feature-name

# Make changes and commit
git add . && git commit -m "feat(scope): description"
git push origin feature/your-feature-name
```

**Essential Commands**: `make dev` | `make test` | `make format` | `make lint`

## 🔄 Deployment Flow
1. PR to `development` → Auto-PR to `UAT` → Auto-PR to `main`
2. **Never push directly to `UAT` or `main`**

## 📚 Documentation
[Full Docs](docs/README.md) | [Contributing](CONTRIBUTING.md) | [Backend](docs/BACKEND_ARCHITECTURE.md) | [Frontend](docs/FRONTEND_ARCHITECTURE.md)
