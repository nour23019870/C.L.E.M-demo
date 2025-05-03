const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');

const store = new Store();

// Keep references to prevent garbage collection
let mainWindow;
const pythonProcesses = {};

// Read app configuration
const appsConfig = JSON.parse(fs.readFileSync(path.join(__dirname, 'config', 'apps.json'), 'utf8'));

function createWindow() {
  // Create icons directory if it doesn't exist
  const iconsDir = path.join(__dirname, 'assets', 'icons', 'app-icons');
  if (!fs.existsSync(iconsDir)) {
    try {
      fs.mkdirSync(iconsDir, { recursive: true });
      console.log(`Created directory: ${iconsDir}`);
    } catch (err) {
      console.error(`Error creating directory: ${err}`);
    }
  }
  
  // Create placeholder icon if icons are missing
  appsConfig.apps.forEach(app => {
    if (app.icon) {
      const iconPath = path.join(__dirname, app.icon);
      if (!fs.existsSync(iconPath)) {
        // Extract just the filename
        const iconFilename = path.basename(app.icon);
        
        // Copy default icon as placeholder
        try {
          const defaultIcon = path.join(__dirname, 'assets', 'icons', 'logo.png');
          if (fs.existsSync(defaultIcon)) {
            fs.copyFileSync(defaultIcon, iconPath);
            console.log(`Created placeholder icon for ${app.name}`);
          }
        } catch (err) {
          console.error(`Error creating icon for ${app.name}: ${err}`);
        }
      }
    }
  });
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: true, 
    transparent: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      // Add a secure Content-Security-Policy to fix the unsafe-eval warning
      webSecurity: true
    },
    icon: path.join(__dirname, 'assets', 'icons', 'logo.png')
  });

  // Set a secure Content Security Policy
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': ["default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self';"]
      }
    });
  });

  // Disable security warnings in the console that trigger console window to appear
  process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true';

  // Load the main HTML file
  mainWindow.loadFile('index.html');
  
  // Only open DevTools when explicitly requested with --dev flag
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    terminateAllPythonProcesses();
  });
}

// Initialize all Python apps in the background
function initializePythonApps() {
  let appsInitialized = 0;
  
  appsConfig.apps.forEach(app => {
    console.log(`Initializing ${app.name}...`);
    
    // Check if app has an initialization script
    if (app.initializationScript) {
      const options = {
        mode: 'text',
        pythonPath: app.pythonPath || 'python', // Use specified Python path or default
        pythonOptions: ['-u'], // Unbuffered output
        scriptPath: app.scriptPath,
        args: app.initArgs || []
      };
      
      try {
        const pyshell = new PythonShell(app.initializationScript, options);
        pythonProcesses[app.id] = pyshell;
        
        pyshell.on('message', (message) => {
          console.log(`[${app.name}] ${message}`);
          // Send initialization status to the renderer
          if (mainWindow) {
            mainWindow.webContents.send('app-status-update', {
              id: app.id,
              status: 'initialized',
              message: message
            });
          }
        });
        
        pyshell.on('error', (err) => {
          console.error(`[${app.name}] Error: ${err}`);
          if (mainWindow) {
            mainWindow.webContents.send('app-status-update', {
              id: app.id,
              status: 'error',
              message: err.toString()
            });
          }
          
          // Count as initialized even if there's an error
          appsInitialized++;
          if (appsInitialized >= appsConfig.apps.length && mainWindow) {
            mainWindow.webContents.send('all-apps-initialized');
          }
        });
        
        pyshell.on('close', () => {
          console.log(`[${app.name}] Process closed`);
          
          // Count this app as initialized
          appsInitialized++;
          if (appsInitialized >= appsConfig.apps.length && mainWindow) {
            mainWindow.webContents.send('all-apps-initialized');
          }
        });
      } catch (err) {
        console.error(`Failed to initialize ${app.name}: ${err}`);
        
        // Still mark this app as initialized for the counter
        appsInitialized++;
        
        // Send initialization status to the renderer
        if (mainWindow) {
          mainWindow.webContents.send('app-status-update', {
            id: app.id,
            status: 'initialized',
            message: 'Ready'
          });
        }
      }
    } else {
      // If there's no initialization script, mark as initialized immediately
      console.log(`${app.name} has no initialization script, marking as ready`);
      
      if (mainWindow) {
        mainWindow.webContents.send('app-status-update', {
          id: app.id,
          status: 'initialized',
          message: 'Ready'
        });
      }
      
      // Count this app as initialized
      appsInitialized++;
    }
  });
  
  // If all apps were immediately marked as initialized, send the all-initialized event
  if (appsInitialized >= appsConfig.apps.length && mainWindow) {
    mainWindow.webContents.send('all-apps-initialized');
  }
}

// Launch a specific app
function launchApp(appId) {
  const app = appsConfig.apps.find(a => a.id === appId);
  
  if (!app) {
    console.error(`App with ID ${appId} not found`);
    return false;
  }
  
  console.log(`Launching ${app.name}...`);
  
  // Validate paths first
  const rootDir = path.resolve(__dirname);
  const scriptPath = path.join(rootDir, app.scriptPath);
  const mainScript = app.mainScript;
  
  // Validate app directory exists
  if (!fs.existsSync(scriptPath)) {
    console.error(`App directory not found: ${scriptPath}`);
    if (mainWindow) {
      mainWindow.webContents.send('app-launch-error', {
        id: appId,
        error: `App directory not found: ${scriptPath}`
      });
    }
    return false;
  }
  
  // Validate main script exists
  const mainScriptPath = path.join(scriptPath, mainScript);
  if (!fs.existsSync(mainScriptPath)) {
    console.error(`Main script not found: ${mainScriptPath}`);
    if (mainWindow) {
      mainWindow.webContents.send('app-launch-error', {
        id: appId,
        error: `Main script not found: ${mainScriptPath}`
      });
    }
    return false;
  }
  
  // Get script directory (might be a subdirectory)
  const mainScriptDir = path.dirname(mainScriptPath);
  const mainScriptName = path.basename(mainScriptPath);
  
  // Setup Python options
  let pythonPath;
  if (app.pythonPath && app.pythonPath.startsWith("env/")) {
    // Relative path, make it absolute
    pythonPath = path.join(rootDir, app.pythonPath);
  } else if (app.pythonPath) {
    // Use provided path
    pythonPath = app.pythonPath;
  } else {
    // Default to env Python
    pythonPath = path.join(rootDir, "env", "Scripts", "python.exe");
  }
  
  // Check if Python executable exists
  if (!fs.existsSync(pythonPath)) {
    console.error(`Python interpreter not found at ${pythonPath}, using default python command`);
    pythonPath = "python";
  }
  
  // List of apps that should open in a separate terminal window
  const terminalApps = ['youtube-download', 'music-download', 'phone-info', 'health-report'];
  
  // Check if this app should be launched in a separate terminal
  if (terminalApps.includes(appId)) {
    // Launch app in a new terminal window
    const { exec } = require('child_process');
    
    // Get the current directory to properly set working directory
    const workingDir = mainScriptDir;
    
    // Create the command to run in a new terminal window
    // For Windows, use 'start cmd /k' to keep the terminal open after the command completes
    let command;
    if (process.platform === 'win32') {
      command = `start cmd /k "cd /d ${workingDir} && "${pythonPath}" ${mainScriptName} ${app.launchArgs ? app.launchArgs.join(' ') : ''}"`; 
    } else if (process.platform === 'darwin') {
      // macOS
      command = `osascript -e 'tell app "Terminal" to do script "cd ${workingDir} && ${pythonPath} ${mainScriptName} ${app.launchArgs ? app.launchArgs.join(' ') : ''}"'`;
    } else {
      // Linux
      command = `gnome-terminal -- bash -c "cd ${workingDir} && ${pythonPath} ${mainScriptName} ${app.launchArgs ? app.launchArgs.join(' ') : ''}; exec bash"}`;
    }
    
    console.log(`Running ${app.name} in a terminal with command: ${command}`);
    
    try {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error(`Failed to launch ${app.name} in terminal: ${error}`);
          if (mainWindow) {
            mainWindow.webContents.send('app-launch-error', {
              id: appId,
              error: error.toString()
            });
          }
          return;
        }
        
        console.log(`[${app.name}] Terminal launched successfully`);
        if (mainWindow) {
          mainWindow.webContents.send('app-launched', {
            id: appId,
            message: `${app.name} launched in a terminal window`
          });
        }
      });
      
      return true;
    } catch (err) {
      console.error(`Failed to launch ${app.name} in terminal: ${err}`);
      if (mainWindow) {
        mainWindow.webContents.send('app-launch-error', {
          id: appId,
          error: err.toString()
        });
      }
      return false;
    }
  } else {
    // Regular app launch with PythonShell
    const options = {
      mode: 'text',
      pythonPath: pythonPath,
      pythonOptions: ['-u'], // Unbuffered output
      scriptPath: mainScriptDir,
      args: app.launchArgs || []
    };
    
    try {
      // If this app already has a running process, terminate it
      if (pythonProcesses[appId]) {
        pythonProcesses[appId].terminate();
        delete pythonProcesses[appId];
      }
      
      console.log(`Running ${app.name} with options:`, options);
      
      const pyshell = new PythonShell(mainScriptName, options);
      pythonProcesses[appId] = pyshell;
      
      pyshell.on('message', (message) => {
        console.log(`[${app.name}] ${message}`);
        // We could forward messages to the renderer if needed
        if (mainWindow) {
          mainWindow.webContents.send('app-message', {
            id: appId,
            message: message
          });
        }
      });
      
      pyshell.on('stderr', (stderr) => {
        console.error(`[${app.name}] Error: ${stderr}`);
        if (mainWindow) {
          mainWindow.webContents.send('app-stderr', {
            id: appId,
            error: stderr
          });
        }
      });
      
      pyshell.on('error', (err) => {
        console.error(`[${app.name}] Error: ${err}`);
        if (mainWindow) {
          mainWindow.webContents.send('app-launch-error', {
            id: appId,
            error: err.toString()
          });
        }
      });
      
      pyshell.on('close', (code) => {
        console.log(`[${app.name}] Process closed with code ${code}`);
        
        delete pythonProcesses[appId];
        
        if (mainWindow) {
          mainWindow.webContents.send('app-closed', {
            id: appId,
            code: code
          });
        }
      });
      
      if (mainWindow) {
        mainWindow.webContents.send('app-launched', {
          id: appId
        });
      }
      
      return true;
    } catch (err) {
      console.error(`Failed to launch ${app.name}: ${err}`);
      if (mainWindow) {
        mainWindow.webContents.send('app-launch-error', {
          id: appId,
          error: err.toString()
        });
      }
      return false;
    }
  }
}

function terminateAllPythonProcesses() {
  Object.values(pythonProcesses).forEach(process => {
    if (process && typeof process.terminate === 'function') {
      process.terminate();
    }
  });
}

// App lifecycle events
app.whenReady().then(() => {
  createWindow();
  
  // Load app configuration and initialize Python apps
  initializePythonApps();
  
  // IPC handlers for renderer communication
  ipcMain.handle('get-apps', () => appsConfig.apps);
  ipcMain.handle('launch-app', (event, appId) => launchApp(appId));
  ipcMain.handle('terminate-app', (event, appId) => {
    if (pythonProcesses[appId]) {
      pythonProcesses[appId].terminate();
      delete pythonProcesses[appId];
      return true;
    }
    return false;
  });
  
  ipcMain.handle('close-app', () => {
    app.quit();
  });
  
  ipcMain.handle('minimize-app', () => {
    if (mainWindow) mainWindow.minimize();
  });
  
  ipcMain.handle('maximize-app', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });
  
  // macOS-specific behavior
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    terminateAllPythonProcesses();
    app.quit();
  }
});

// Clean up before exit
app.on('before-quit', () => {
  terminateAllPythonProcesses();
});