# ProjectMeats3 - Quick Setup Reference

**🚀 For complete deployment guide, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

## 🔄 Centralized Configuration System

ProjectMeats uses a centralized environment configuration system that integrates with the CI/CD pipeline for better maintainability and deployment management.

### Quick Setup (Recommended)
```bash
# Set up development environment
python config/manage_env.py setup development

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Start development servers
make dev
```

### Alternative Setup (Legacy)
```bash
python setup.py
```

For complete configuration documentation, see: **[docs/ENVIRONMENT_GUIDE.md](docs/ENVIRONMENT_GUIDE.md)**

## 🚨 Solving "Authentication credentials were not provided"

This error typically occurs when the AI Assistant backend isn't properly configured. Here's the **fastest solution**:

### Step 1: Run the Interactive Setup
```bash
cd ProjectMeats3
python setup.py
```

This will guide you through:
- ✅ Django backend setup
- ✅ React frontend setup
- ✅ Database configuration  
- ✅ Environment variables
- ✅ Dependencies installation

### Step 2: Start the Servers
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend  
cd frontend
npm start
```

### Step 3: Access the Application
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000  
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

## Alternative Quick Fixes

### Fix 1: Check Environment Files
```bash
# Verify files exist
ls -la backend/.env
ls -la frontend/.env.local

# If missing, copy examples:
cp backend/.env.example backend/.env
```

### Fix 2: Create Admin User
```bash
cd backend
python manage.py createsuperuser
```

### Fix 3: Verify Django Settings
```bash
cd backend
python manage.py check
```

### Fix 4: Reset Everything
```bash
# Delete old config and start fresh
rm backend/.env
rm frontend/.env.local
rm backend/db.sqlite3

# Run setup again
python setup.py
```

## What the Setup Configures

### Backend (.env)
```bash
# Database  
DATABASE_URL=sqlite:///db.sqlite3

# CORS (fixes frontend connection)
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Django Settings
SECRET_KEY=auto-generated-secure-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env.local)
```bash
# API Connection
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
```

## Enhanced AI Assistant Features

This version includes the latest AI Assistant improvements from PR #63:

### Fixed Issues ✅
- **HTTP 404 Errors**: Fixed API endpoint URLs (/ai-assistant/ai-chat/chat/)
- **Intelligent Responses**: Enhanced with meat industry-specific AI responses
- **Modern UI**: Complete Copilot-style interface with integrated file upload
- **Drag & Drop**: Seamless document upload experience

### New Features ✅
- **Integrated File Upload**: Attachment button directly in message input
- **Drag & Drop Support**: Drop files anywhere in chat area
- **Visual Feedback**: Animations, loading states, error handling
- **File Validation**: Support for PDF, images, documents with size limits
- **Enhanced UX**: Professional error messages and user guidance

## Common Issues

### Issue: "Module not found: django"
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "npm command not found"
- Install Node.js from [nodejs.org](https://nodejs.org)
- Restart terminal

### Issue: "Permission denied"
```bash
# Linux/Mac - fix permissions
chmod +x setup.py
```

### Issue: CORS Errors
- Make sure both backend and frontend are running
- Check CORS_ALLOWED_ORIGINS in backend/.env
- Verify REACT_APP_API_BASE_URL in frontend/.env.local

## Platform-Specific Commands

### Windows
```cmd
python setup.py
```

### Linux/macOS
```bash
python setup.py
# or
make setup
```

### Manual Setup
```bash
# Backend only
python setup.py --backend

# Frontend only  
python setup.py --frontend
```

## Validation

Test your setup by visiting:
1. **Frontend**: http://localhost:3000 - Should show AI chat interface
2. **Backend**: http://localhost:8000/api/docs/ - Should show API documentation
3. **Test Chat**: Send a message in the frontend, should get AI response

## AI Assistant Demo Features

Try these commands to test the enhanced AI responses:

- "Show me supplier performance metrics"
- "Help me analyze purchase orders"
- "Review customer order patterns"
- "Check inventory levels"
- "Generate pricing analysis"
- Upload a document (drag & drop supported!)

## Need Help?

1. **Check logs:**
   ```bash
   # Backend logs
   cd backend && python manage.py runserver --verbosity=2
   
   # Frontend logs
   cd frontend && npm start
   ```

2. **Reset and retry:**
   ```bash
   python setup.py
   ```

3. **Documentation:**
   - `README.md` - Project overview
   - API documentation at http://localhost:8000/api/docs/

The setup script is designed to solve 99% of configuration issues automatically. If you're still having problems, check the error messages for specific guidance.