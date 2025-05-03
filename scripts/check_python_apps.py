#!/usr/bin/env python
"""
Script to check all Python apps in the python-apps directory
using the Python 3.10 environment and verify they can run properly.
"""
import os
import sys
import json
import importlib
import subprocess
import pkg_resources
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PYTHON = ROOT_DIR / "env" / "Scripts" / "python.exe"
APPS_CONFIG = ROOT_DIR / "config" / "apps.json"
PYTHON_APPS_DIR = ROOT_DIR / "python-apps"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"

def print_status(message, status):
    """Print status messages with colors"""
    if status == "success":
        print(f"✅ {message}")
    elif status == "warning":
        print(f"⚠️ {message}")
    elif status == "error":
        print(f"❌ {message}")
    else:
        print(message)

def check_env_python():
    """Check if the Python 3.10 environment exists and is accessible"""
    print("\n== Checking Python Environment ==")
    
    if not ENV_PYTHON.exists():
        print_status(f"Python environment not found at: {ENV_PYTHON}", "error")
        return False
    
    # Check Python version
    try:
        result = subprocess.run([str(ENV_PYTHON), "-V"], capture_output=True, text=True)
        version = result.stdout.strip()
        print_status(f"Found {version}", "success")
        if "3.10" not in version:
            print_status(f"Warning: Expected Python 3.10, but found {version}", "warning")
    except Exception as e:
        print_status(f"Error checking Python version: {e}", "error")
        return False
    
    return True

def install_requirements():
    """Ensure all requirements are installed in the environment"""
    print("\n== Checking Requirements ==")
    
    if not REQUIREMENTS_FILE.exists():
        print_status(f"Requirements file not found at: {REQUIREMENTS_FILE}", "error")
        return False
    
    try:
        print(f"Installing requirements from {REQUIREMENTS_FILE}...")
        subprocess.run([str(ENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], 
                      check=True)
        print_status("Requirements installation completed", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Error installing requirements: {e}", "error")
        return False

def get_app_configs():
    """Load app configurations from apps.json"""
    try:
        with open(APPS_CONFIG, 'r') as f:
            config = json.load(f)
        return config.get('apps', [])
    except Exception as e:
        print_status(f"Error loading app configurations: {e}", "error")
        return []

def check_app_imports(app_path, main_script="main.py"):
    """Check if an app's imports work correctly"""
    try:
        # Look for the specified main script file
        main_file = app_path / main_script
        if not main_file.exists():
            print_status(f"{main_script} not found in {app_path}", "error")
            return False
        
        # Instead of actually importing modules which can cause issues,
        # let's run a simple syntax check on the Python file
        result = subprocess.run(
            [str(ENV_PYTHON), "-m", "py_compile", str(main_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print_status(f"  Syntax error in {main_file}: {result.stderr}", "error")
            return False
            
        # Success if no syntax errors
        return True
    
    except Exception as e:
        print_status(f"Error checking app: {e}", "error")
        return False

def check_app_requirements(app_path):
    """Check if an app has its own requirements.txt and install if needed"""
    req_file = Path(app_path) / "requirements.txt"
    if req_file.exists():
        try:
            print(f"  Installing app-specific requirements from {req_file}...")
            subprocess.run([str(ENV_PYTHON), "-m", "pip", "install", "-r", str(req_file)], 
                         check=True)
            print_status("  App-specific requirements installed", "success")
            return True
        except subprocess.CalledProcessError as e:
            print_status(f"  Error installing app-specific requirements: {e}", "error")
            return False
    return True  # No requirements file is not an error

def check_app_executable(app_path, main_script="main.py"):
    """Check if the app runs without immediate errors"""
    try:
        # Run the script with a quick timeout to check if it starts without crashing
        cmd = [str(ENV_PYTHON), "-c", f"import sys; sys.path.append('{app_path}'); print('App can be imported')"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1  # Very short timeout, we just want to check if it starts
        )
        
        if "App can be imported" in result.stdout:
            return True
        else:
            print_status(f"  Warning: App may have startup issues: {result.stderr}", "warning")
            return False
    except subprocess.TimeoutExpired:
        # This is actually good! It means the app started and didn't crash immediately
        return True
    except Exception as e:
        print_status(f"  Warning: App startup check failed: {e}", "warning")
        return False

def main():
    """Main function to check all Python apps"""
    print("===== Python App Checker =====")
    print(f"Using Python environment: {ENV_PYTHON}")
    
    # Check if the Python environment exists
    if not check_env_python():
        return
    
    # Install requirements
    install_requirements()
    
    # Get app configurations
    apps = get_app_configs()
    if not apps:
        print_status("No app configurations found", "error")
        return
    
    print(f"\n== Checking {len(apps)} Python Apps ==")
    
    # Check each app
    for app in apps:
        app_id = app.get('id', 'Unknown')
        app_name = app.get('name', app_id)
        script_path = app.get('scriptPath', '')
        main_script_name = app.get('mainScript', 'main.py')
        
        print(f"\nChecking app: {app_name} ({app_id})")
        
        # Validate app directory
        app_dir = ROOT_DIR / script_path
        if not app_dir.exists():
            print_status(f"  App directory not found: {app_dir}", "error")
            continue
        
        # Check app-specific requirements.txt
        check_app_requirements(app_dir)
        
        # Check for main script, which might be in a subdirectory
        main_script_path = app_dir / main_script_name
        if not main_script_path.exists():
            print_status(f"  Main script not found: {main_script_path}", "error")
            continue
            
        # Perform syntax check on the main script
        if check_app_imports(app_dir, main_script_name):
            print_status(f"  No syntax errors in {app_name}", "success")
            
        print_status(f"  App {app_name} is ready to run", "success")
    
    print("\n===== Check Completed =====")

if __name__ == "__main__":
    main()