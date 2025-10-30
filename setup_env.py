#!/usr/bin/env python3
"""
ProjectMeats Cross-Platform Setup Script
======================================

This script provides a unified setup experience across Windows, macOS, and Linux.
It handles environment setup, dependency installation, initial configuration, and superuser creation.

Usage:
    python setup_env.py              # Full setup (backend + frontend)
    python setup_env.py --backend    # Backend only
    python setup_env.py --frontend   # Frontend only
    python setup_env.py --help       # Show help

Features:
- Cross-platform compatibility (Windows, macOS, Linux)
- Automatic platform detection
- Error handling and validation
- Progress reporting
- Dependency checking
- Superuser creation (credentials from environment variables)
- Comprehensive test data creation
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path


class Colors:
    """ANSI color codes for cross-platform terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if platform.system() == "Windows" and not os.environ.get('TERM'):
            for attr in dir(cls):
                if not attr.startswith('_') and attr != 'disable_on_windows':
                    setattr(cls, attr, '')


class ProjectMeatsSetup:
    """Main setup class for ProjectMeats"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Disable colors on unsupported Windows terminals
        if self.is_windows:
            Colors.disable_on_windows()
    
    def log(self, message, level="INFO", color=None):
        """Enhanced logging with colors and levels"""
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE
        }
        
        if color is None:
            color = color_map.get(level, Colors.WHITE)
        
        timestamp = ""  # Keep simple for now
        print(f"{color}[{level}]{Colors.END} {message}")
    
    def run_command(self, command, cwd=None, shell=None, check=True):
        """Run a command with proper error handling"""
        if cwd is None:
            cwd = self.project_root
        
        if shell is None:
            shell = self.is_windows
        
        try:
            self.log(f"Running: {command}", "INFO", Colors.CYAN)
            
            # Handle different command formats
            if isinstance(command, str):
                if shell:
                    result = subprocess.run(command, shell=True, cwd=cwd, 
                                         capture_output=False, check=check)
                else:
                    result = subprocess.run(command.split(), cwd=cwd, 
                                         capture_output=False, check=check)
            else:
                result = subprocess.run(command, cwd=cwd, 
                                     capture_output=False, check=check)
            
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed with exit code {e.returncode}: {command}", "ERROR")
            return False
        except FileNotFoundError:
            self.log(f"Command not found: {command}", "ERROR")
            return False
    
    def check_dependency(self, command, version_flag="--version", min_version=None):
        """Check if a dependency is installed"""
        try:
            # Use shutil.which to properly resolve command path (handles .cmd/.bat on Windows)
            command_path = shutil.which(command)
            if command_path is None:
                self.log(f"✗ {command} not found", "ERROR")
                return False
            
            result = subprocess.run([command_path, version_flag], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_output = result.stdout.strip()
                self.log(f"✓ {command} found: {version_output.split()[0] if version_output else 'installed'}", 
                        "SUCCESS")
                return True
            else:
                self.log(f"✗ {command} not found or not working", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            self.log(f"✗ {command} not found", "ERROR")
            return False
    
    def copy_env_file(self, source, destination):
        """Copy environment file if it doesn't exist"""
        source_path = Path(source)
        dest_path = Path(destination)
        
        if dest_path.exists():
            self.log(f"ℹ️  {dest_path.name} already exists", "WARNING")
            return True
        
        if not source_path.exists():
            self.log(f"Source file not found: {source_path}", "ERROR")
            return False
        
        try:
            shutil.copy2(source_path, dest_path)
            self.log(f"✓ Created {dest_path.name}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to copy {source_path} to {dest_path}: {e}", "ERROR")
            return False
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log("🔍 Checking system prerequisites...", "STEP")
        
        prerequisites = []
        
        # Check Python
        if self.check_dependency("python", "--version"):
            prerequisites.append("python")
        elif self.check_dependency("python3", "--version"):
            prerequisites.append("python3")
        else:
            self.log("Python 3.9+ is required. Please install Python.", "ERROR")
            return False
        
        # Check Node.js and npm
        if not self.check_dependency("node", "--version"):
            self.log("Node.js 16+ is required. Please install Node.js from https://nodejs.org/", "ERROR")
            return False
        
        if not self.check_dependency("npm", "--version"):
            self.log("npm is required and should come with Node.js", "ERROR")
            return False
        
        # Check pip
        pip_cmd = "pip3" if "python3" in prerequisites else "pip"
        if not self.check_dependency(pip_cmd, "--version"):
            self.log("pip is required for Python package installation", "ERROR")
            return False
        
        # Optional: Check git
        if self.check_dependency("git", "--version"):
            self.log("✓ Git available for version control", "SUCCESS")
        else:
            self.log("ℹ️  Git not found - version control won't be available", "WARNING")
        
        self.log("✅ Prerequisites check completed", "SUCCESS")
        return True
    
    def setup_backend(self):
        """Setup Django backend"""
        self.log("🔧 Setting up Django backend...", "STEP")
        
        if not self.backend_dir.exists():
            self.log(f"Backend directory not found: {self.backend_dir}", "ERROR")
            return False
        
        # Set up environment configuration using centralized system
        config_manager = self.project_root / "config" / "manage_env.py"
        if config_manager.exists():
            self.log("Using centralized environment configuration...", "INFO")
            python_cmd = "python3" if shutil.which("python3") else "python"
            env_cmd = f"{python_cmd} {config_manager} setup development"
            if self.run_command(env_cmd, cwd=self.project_root):
                self.log("✓ Environment configured using centralized system", "SUCCESS")
            else:
                self.log("Failed to set up centralized environment, falling back to legacy", "WARNING")
                # Fallback to legacy method
                env_source = self.backend_dir / ".env.example"
                env_dest = self.backend_dir / ".env"
                if not self.copy_env_file(env_source, env_dest):
                    return False
        else:
            # Legacy environment setup
            env_source = self.backend_dir / ".env.example"
            env_dest = self.backend_dir / ".env"
            if not self.copy_env_file(env_source, env_dest):
                return False
        
        # Install Python dependencies
        self.log("📦 Installing Python dependencies...", "INFO")
        
        # Determine Python and pip commands
        python_cmd = "python3" if shutil.which("python3") else "python"
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"
        
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            self.log(f"Requirements file not found: {requirements_file}", "ERROR")
            return False
        
        # Install dependencies
        install_cmd = f"{pip_cmd} install --timeout 30 -r requirements.txt"
        if not self.run_command(install_cmd, cwd=self.backend_dir):
            self.log("Failed to install Python dependencies", "ERROR")
            return False
        
        # Run migrations
        self.log("🗃️  Running database migrations...", "INFO")
        migrate_cmd = f"{python_cmd} manage.py migrate"
        if not self.run_command(migrate_cmd, cwd=self.backend_dir):
            self.log("Failed to run migrations", "ERROR")
            return False
        
        # Create superuser and root tenant
        self.log("👤 Setting up superuser and root tenant...", "INFO")
        superuser_cmd = f"{python_cmd} manage.py create_super_tenant"
        if not self.run_command(superuser_cmd, cwd=self.backend_dir):
            self.log("Failed to create superuser (this is non-fatal)", "WARNING")
            # Continue anyway - superuser creation failure shouldn't block setup
        
        self.log("✅ Backend setup complete!", "SUCCESS")
        return True
    
    def setup_frontend(self):
        """Setup React frontend"""
        self.log("🔧 Setting up React frontend...", "STEP")
        
        if not self.frontend_dir.exists():
            self.log(f"Frontend directory not found: {self.frontend_dir}", "ERROR")
            return False
        
        # Check package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.log(f"package.json not found: {package_json}", "ERROR")
            return False
        
        # Install Node.js dependencies
        self.log("📦 Installing Node.js dependencies...", "INFO")
        
        if not self.run_command("npm install", cwd=self.frontend_dir):
            self.log("Failed to install Node.js dependencies", "ERROR") 
            return False
        
        # Copy environment file if it exists
        env_source = self.frontend_dir / ".env.example"
        env_dest = self.frontend_dir / ".env.local"
        
        if env_source.exists():
            self.copy_env_file(env_source, env_dest)
        else:
            # Create a basic environment file
            try:
                with open(env_dest, 'w', encoding='utf-8') as f:
                    f.write("# React Environment Variables\n")
                    f.write("REACT_APP_API_BASE_URL=https://meatscentral/api/v1\n")
                    f.write("REACT_APP_ENVIRONMENT=development\n")
                self.log(f"✓ Created basic {env_dest.name}", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to create {env_dest}: {e}", "WARNING")
        
        self.log("✅ Frontend setup complete!", "SUCCESS")
        return True
    
    def print_next_steps(self):
        """Print helpful next steps"""
        self.log("\n🎉 Setup completed successfully!", "SUCCESS", Colors.BOLD)
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print(f"{Colors.GREEN}1.{Colors.END} Start the backend server:")
        if self.is_windows:
            print(f"   {Colors.CYAN}cd backend && python manage.py runserver{Colors.END}")
        else:
            print(f"   {Colors.CYAN}make backend{Colors.END} or {Colors.CYAN}cd backend && python manage.py runserver{Colors.END}")
        
        print(f"\n{Colors.GREEN}2.{Colors.END} Start the frontend server:")
        if self.is_windows:
            print(f"   {Colors.CYAN}cd frontend && npm start{Colors.END}")
        else:
            print(f"   {Colors.CYAN}make frontend{Colors.END} or {Colors.CYAN}cd frontend && npm start{Colors.END}")
        
        print(f"\n{Colors.GREEN}3.{Colors.END} Access the application:")
        print(f"   {Colors.CYAN}Backend API: http://localhost:8000{Colors.END}")
        print(f"   {Colors.CYAN}Frontend:    http://localhost:3000{Colors.END}")
        print(f"   {Colors.CYAN}API Docs:    http://localhost:8000/api/docs/{Colors.END}")
        print(f"   {Colors.CYAN}Admin Panel: http://localhost:8000/admin/{Colors.END}")
        
        if not self.is_windows:
            print(f"\n{Colors.BOLD}Available Make Commands:{Colors.END}")
            print(f"   {Colors.CYAN}make dev{Colors.END}      - Start both servers")
            print(f"   {Colors.CYAN}make test{Colors.END}     - Run all tests")
            print(f"   {Colors.CYAN}make docs{Colors.END}     - Generate API documentation")
            print(f"   {Colors.CYAN}make clean{Colors.END}    - Clean build artifacts")
    
    def main(self):
        """Main setup function"""
        parser = argparse.ArgumentParser(
            description="ProjectMeats3 Cross-Platform Setup Script",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        
        parser.add_argument("--backend", action="store_true", 
                           help="Setup backend only")
        parser.add_argument("--frontend", action="store_true", 
                           help="Setup frontend only") 
        parser.add_argument("--skip-prereqs", action="store_true",
                           help="Skip prerequisite checks")
        
        args = parser.parse_args()
        
        # Welcome message
        self.log("🚀 ProjectMeats3 Setup Script", "STEP", Colors.BOLD)
        self.log(f"Platform: {platform.system()} {platform.release()}", "INFO")
        self.log(f"Python: {sys.version.split()[0]}", "INFO")
        self.log(f"Working directory: {self.project_root}", "INFO")
        
        # Check prerequisites
        if not args.skip_prereqs and not self.check_prerequisites():
            self.log("Prerequisites not met. Please install required dependencies.", "ERROR")
            return 1
        
        # Determine what to setup
        setup_backend = args.backend or not args.frontend
        setup_frontend = args.frontend or not args.backend
        
        success = True
        
        # Setup backend
        if setup_backend:
            if not self.setup_backend():
                success = False
        
        # Setup frontend  
        if setup_frontend:
            if not self.setup_frontend():
                success = False
        
        if success:
            self.print_next_steps()
            return 0
        else:
            self.log("Setup completed with errors. Please check the messages above.", "ERROR")
            return 1


if __name__ == "__main__":
    setup = ProjectMeatsSetup()
    sys.exit(setup.main())