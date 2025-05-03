<<<<<<< HEAD
@echo off
echo CLEM Environment Setup Tool
echo ============================
echo.
echo This script will set up all required Python environments for CLEM.
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10 and try again.
    exit /b 1
)

REM Verify Python version (should be 3.10.x)
python -c "import sys; version=sys.version_info; exit(0 if (version.major == 3 and version.minor == 10) else 1)"
if %ERRORLEVEL% neq 0 (
    echo Warning: Python version is not 3.10.x which is recommended for CLEM.
    echo Current Python version:
    python --version
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if %ERRORLEVEL% neq 1 exit /b 1
)

REM Install virtualenv if not already installed
pip show virtualenv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing virtualenv...
    pip install virtualenv
)

REM Define the applications that need environment setup
set "apps=air-writing signLang emotions media_control"

REM Setup main root environment
echo.
echo Setting up main CLEM environment...
if not exist env (
    python -m venv env
)
call env\Scripts\activate
pip install -r requirements.txt
echo Main environment setup complete.
call env\Scripts\deactivate

REM Setup individual app environments
for %%a in (%apps%) do (
    echo.
    echo Setting up environment for: %%a
    if exist "python-apps\%%a\requirements.txt" (
        if not exist "python-apps\%%a\env" (
            python -m venv "python-apps\%%a\env"
        )
        call "python-apps\%%a\env\Scripts\activate"
        pip install -r "python-apps\%%a\requirements.txt"
        call "python-apps\%%a\env\Scripts\deactivate"
        echo Environment setup for %%a completed.
    ) else (
        echo No requirements.txt found for %%a. Skipping.
    )
)

echo.
echo ============================
echo All environments are set up successfully!
echo You can now run CLEM using CLEM-Launcher.vbs
echo ============================
=======
@echo off
echo CLEM Environment Setup Tool
echo ============================
echo.
echo This script will set up all required Python environments for CLEM.
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10 and try again.
    exit /b 1
)

REM Verify Python version (should be 3.10.x)
python -c "import sys; version=sys.version_info; exit(0 if (version.major == 3 and version.minor == 10) else 1)"
if %ERRORLEVEL% neq 0 (
    echo Warning: Python version is not 3.10.x which is recommended for CLEM.
    echo Current Python version:
    python --version
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if %ERRORLEVEL% neq 1 exit /b 1
)

REM Install virtualenv if not already installed
pip show virtualenv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing virtualenv...
    pip install virtualenv
)

REM Define the applications that need environment setup
set "apps=air-writing signLang emotions media_control"

REM Setup main root environment
echo.
echo Setting up main CLEM environment...
if not exist env (
    python -m venv env
)
call env\Scripts\activate
pip install -r requirements.txt
echo Main environment setup complete.
call env\Scripts\deactivate

REM Setup individual app environments
for %%a in (%apps%) do (
    echo.
    echo Setting up environment for: %%a
    if exist "python-apps\%%a\requirements.txt" (
        if not exist "python-apps\%%a\env" (
            python -m venv "python-apps\%%a\env"
        )
        call "python-apps\%%a\env\Scripts\activate"
        pip install -r "python-apps\%%a\requirements.txt"
        call "python-apps\%%a\env\Scripts\deactivate"
        echo Environment setup for %%a completed.
    ) else (
        echo No requirements.txt found for %%a. Skipping.
    )
)

echo.
echo ============================
echo All environments are set up successfully!
echo You can now run CLEM using CLEM-Launcher.vbs
echo ============================
>>>>>>> 5e9a3670482b7bf8a2a6994e351bb2bbbac3da10
pause