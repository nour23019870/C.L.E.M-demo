#!/usr/bin/env python
"""
Script to run Python apps from the python-apps directory
using the Python 3.10 environment.
"""
import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PYTHON = ROOT_DIR / "env" / "Scripts" / "python.exe"
APPS_CONFIG = ROOT_DIR / "config" / "apps.json"

def load_app_configs():
    """Load app configurations from apps.json"""
    try:
        with open(APPS_CONFIG, 'r') as f:
            config = json.load(f)
        return config.get('apps', [])
    except Exception as e:
        print(f"Error loading app configurations: {e}")
        return []

def list_available_apps():
    """List all available apps from the config"""
    apps = load_app_configs()
    if not apps:
        print("No apps found in configuration.")
        return
    
    print("\nAvailable Apps:")
    print("---------------")
    for i, app in enumerate(apps, 1):
        app_id = app.get('id', 'Unknown')
        app_name = app.get('name', app_id)
        app_desc = app.get('description', 'No description')
        print(f"{i}. {app_name} ({app_id}): {app_desc}")
    print()

def run_app(app_id):
    """Run a specific app by its ID"""
    apps = load_app_configs()
    app = next((a for a in apps if a.get('id') == app_id), None)
    
    if not app:
        print(f"App with ID '{app_id}' not found.")
        return False
    
    app_name = app.get('name', app_id)
    script_path = app.get('scriptPath', '')
    main_script = app.get('mainScript', 'main.py')
    python_path = app.get('pythonPath', str(ENV_PYTHON))
    launch_args = app.get('launchArgs', [])
    
    print(f"Launching {app_name}...")
    print(f"  • Script path: {script_path}")
    print(f"  • Main script: {main_script}")
    print(f"  • Python path: {python_path}")
    
    # Validate app directory
    app_dir = ROOT_DIR / script_path
    if not app_dir.exists():
        print(f"ERROR: App directory not found: {app_dir}")
        return False
    
    # Validate main script - handle subdirectories properly
    main_script_path = app_dir / main_script
    if not main_script_path.exists():
        print(f"ERROR: Main script not found: {main_script_path}")
        return False
    
    # Get the directory containing the main script (might be a subdirectory)
    main_script_dir = main_script_path.parent
    main_script_name = main_script_path.name

    # Use the specified Python interpreter or fall back to the env Python
    if python_path.startswith("env/"):
        # Relative path, make it absolute
        python_exe = ROOT_DIR / python_path
    else:
        # Absolute path or just a command
        python_exe = Path(python_path)

    # If not found, use default env Python
    if not python_exe.exists():
        print(f"WARNING: Python interpreter not found at {python_exe}, using default")
        python_exe = ENV_PYTHON
    
    print(f"Running {app_name} with {python_exe}...")
    print(f"Working directory: {main_script_dir}")
    
    try:
        # Set up environment variables if needed
        env = os.environ.copy()
        # Add both the app dir and main script dir to PYTHONPATH
        env['PYTHONPATH'] = f"{app_dir}{os.pathsep}{main_script_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
        
        # Change to the directory containing the main script
        original_dir = os.getcwd()
        os.chdir(main_script_dir)
        
        # Create command to run with any launch arguments
        cmd = [str(python_exe), str(main_script_name)] + launch_args
        print(f"Running command: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, env=env)
        
        print(f"{app_name} is now running. Press Ctrl+C to stop.")
        try:
            process.wait()
        except KeyboardInterrupt:
            print(f"\nStopping {app_name}...")
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Return to original directory
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"ERROR running {app_name}: {e}")
        import traceback
        traceback.print_exc()
        # Try to return to original directory
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

def run_all_apps():
    """Run all available apps in sequence"""
    apps = load_app_configs()
    
    if not apps:
        print("No apps found in configuration.")
        return
    
    print(f"Running all {len(apps)} apps in sequence...\n")
    
    for app in apps:
        app_id = app.get('id')
        run_app(app_id)
        print("\nPress Enter to continue to the next app or Ctrl+C to exit")
        try:
            input()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    """Main function to run Python apps"""
    parser = argparse.ArgumentParser(description='Run Python apps using the Python 3.10 environment')
    parser.add_argument('--list', '-l', action='store_true', help='List available apps')
    parser.add_argument('--app', '-a', type=str, help='ID of the app to run')
    parser.add_argument('--check-all', '-c', action='store_true', help='Check all apps before running')
    parser.add_argument('--run-all', '-r', action='store_true', help='Run all apps in sequence')
    
    args = parser.parse_args()
    
    if args.check_all:
        # Run the check_python_apps script first
        check_script = ROOT_DIR / "scripts" / "check_python_apps.py"
        if check_script.exists():
            print("Checking all Python apps first...\n")
            subprocess.run([str(ENV_PYTHON), str(check_script)])
        else:
            print("Check script not found. Continuing without checking.")
    
    if args.list:
        list_available_apps()
        return
        
    if args.run_all:
        run_all_apps()
        return
    
    if args.app:
        run_app(args.app)
    else:
        list_available_apps()
        try:
            choice = input("Enter app ID or number to run (or 'q' to quit): ")
            if choice.lower() == 'q':
                return
            
            # Check if the input is a number
            if choice.isdigit():
                apps = load_app_configs()
                index = int(choice) - 1
                if 0 <= index < len(apps):
                    run_app(apps[index].get('id'))
                else:
                    print("Invalid app number.")
            else:
                run_app(choice)
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()