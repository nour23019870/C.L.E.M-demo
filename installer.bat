@echo off
echo CLEM Environment Setup Tool
echo ============================
echo.
echo This script will set up all required Python environments for CLEM.
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo After installation, restart this script.
    goto :error
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo npm is not installed or not in PATH.
    echo Please ensure Node.js is properly installed.
    goto :error
)

REM Install Node.js dependencies
echo Installing required Node.js packages...
call npm init -y >nul 2>nul
echo Installing python-shell and other required packages...
call npm install python-shell@5.0.0 electron-store@8.1.0 node-hide-console-window@2.2.0 --save
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install Node.js packages.
    echo Please check your Node.js installation and internet connection.
    goto :error
) else (
    echo Node.js packages installed successfully.
    if not exist "node_modules" (
        echo Warning: node_modules folder was not created.
        echo Trying alternate installation method...
        call npm install --production
        if not exist "node_modules" (
            echo Error: Failed to create node_modules folder.
            goto :error
        )
    )
)

REM Check if Python310 folder exists
if not exist "Python310\python.exe" (
    echo Python310 folder not found.
    echo Downloading Python 3.10 to local folder...
    
    REM Create temporary directory for download
    mkdir temp 2>nul
    
    REM Download Python 3.10.11 installer
    echo Downloading Python 3.10.11...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile 'temp\python310.zip'}"
    
    if not exist "temp\python310.zip" (
        echo Failed to download Python. Please check your internet connection.
        echo Please install Python 3.10 manually from https://www.python.org/downloads/
        exit /b 1
    )
    
    echo Extracting Python 3.10...
    powershell -Command "& {Expand-Archive -Path 'temp\python310.zip' -DestinationPath 'Python310' -Force}"
)

REM Fix python310._pth file regardless of whether we just downloaded Python or not
echo Configuring Python paths...
(
    echo python310.zip
    echo .
    echo 
    echo import site
) > "Python310\python310._pth"

REM Check if pip exists, if not install it
if not exist "Python310\Scripts\pip.exe" (
    echo Downloading pip installer...
    mkdir temp 2>nul
    powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'temp\get-pip.py'}"
    
    echo Installing pip...
    "Python310\python.exe" "temp\get-pip.py"
    
    REM Clean up
    rmdir /S /Q temp 2>nul
)

echo Using Python 3.10 from the Python310 folder.
set "PYTHON_CMD=Python310\python.exe"
set "PIP_CMD=Python310\Scripts\pip.exe"

REM Test if pip is working
echo Testing pip installation...
%PYTHON_CMD% -m pip --version
if %ERRORLEVEL% neq 0 (
    echo Error: pip is not working correctly.
    echo This may be due to an issue with the Python installation.
    echo Please try downloading Python 3.10 manually from https://www.python.org/downloads/
    goto :error
)

REM Install virtualenv if not already installed
%PIP_CMD% show virtualenv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing virtualenv...
    %PIP_CMD% install virtualenv
)

REM Define the applications that need environment setup
set "apps=air-writing signLang emotions media_control"

REM Setup main root environment
echo.
echo Setting up main CLEM environment...
if not exist env (
    %PYTHON_CMD% -m virtualenv env
)
call env\Scripts\activate



echo Installing the rest of the requirements...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo WARNING: Some packages may have failed to install in the main environment
    echo Attempting to install packages individually...
    
    for /f "tokens=*" %%p in ('type requirements.txt') do (
        echo Installing package: %%p
        pip install %%p
    )
)
echo Main environment setup complete.
call env\Scripts\deactivate

REM Setup individual app environments
for %%a in (%apps%) do (
    echo.
    echo Setting up environment for: %%a
    if exist "python-apps\%%a\requirements.txt" (
        if not exist "python-apps\%%a\env" (
            %PYTHON_CMD% -m virtualenv "python-apps\%%a\env"
            if %ERRORLEVEL% neq 0 (
                echo ERROR: Failed to create virtual environment for %%a
                echo Please check the Python installation and try again.
                goto :error
            )
        )
        call "python-apps\%%a\env\Scripts\activate"
        
        echo Installing requirements from requirements.txt file...
        pip install -r "python-apps\%%a\requirements.txt"
        if %ERRORLEVEL% neq 0 (
            echo WARNING: Some packages may have failed to install for %%a
            echo Attempting to install packages individually...
            
            for /f "tokens=*" %%p in ('type "python-apps\%%a\requirements.txt"') do (
                if not "%%p"=="" (
                    if not "%%p:~0,1%"=="#" (
                        echo Installing package: %%p
                        pip install %%p -q
                    )
                )
            )
        )
        
        call "python-apps\%%a\env\Scripts\deactivate"
        echo Environment setup for %%a completed.
    ) else (
        echo No requirements.txt found for %%a. Skipping.
    )
)

echo.
echo ============================
echo All environments are set up successfully!
echo You can now run CLEM using main.bat
echo ============================
goto :end

:error
echo.
echo ============================
echo ERROR: Setup failed. Please check the error messages above.
echo ============================

:end
echo Press any key to exit...
pause > nul
