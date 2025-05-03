// app-manager.js - Helper module for managing Python processes

const { PythonShell } = require('python-shell');
const path = require('path');
const fs = require('fs');
const EventEmitter = require('events');

class AppManager extends EventEmitter {
  constructor(configPath) {
    super();
    this.configPath = configPath;
    this.apps = [];
    this.processes = {};
    this.initialized = false;
    this.loadConfig();
  }

  // Load app configuration
  loadConfig() {
    try {
      const configData = fs.readFileSync(this.configPath, 'utf8');
      this.apps = JSON.parse(configData).apps;
      this.initialized = true;
      this.emit('config-loaded', this.apps);
    } catch (error) {
      console.error(`Failed to load app configuration: ${error}`);
      this.emit('error', 'Failed to load app configuration');
    }
  }

  // Get the list of apps
  getApps() {
    return this.apps;
  }

  // Initialize all apps in the background
  initializeApps() {
    if (!this.initialized) {
      throw new Error('App manager not initialized');
    }

    this.apps.forEach(app => this.initializeApp(app.id));
    this.emit('initialization-started', this.apps.length);
  }

  // Initialize a specific app
  initializeApp(appId) {
    const app = this.apps.find(a => a.id === appId);
    if (!app) {
      this.emit('app-init-error', { id: appId, error: 'App not found' });
      return false;
    }

    // Skip if no initialization script
    if (!app.initializationScript) {
      this.emit('app-initialized', { id: appId, message: 'No initialization needed' });
      return true;
    }

    try {
      // Configure PythonShell options
      const options = {
        mode: 'text',
        pythonPath: app.pythonPath || 'python',
        pythonOptions: ['-u'], // Unbuffered output
        scriptPath: app.scriptPath,
        args: app.initArgs || []
      };

      // Start initialization process
      const pyshell = new PythonShell(app.initializationScript, options);
      this.processes[appId] = {
        process: pyshell,
        status: 'initializing',
        type: 'init'
      };

      // Handle process events
      pyshell.on('message', (message) => {
        this.emit('app-message', { id: appId, message, type: 'init' });
      });

      pyshell.on('stderr', (err) => {
        console.error(`[${app.name}] Error: ${err}`);
        this.emit('app-error', { id: appId, error: err, type: 'init' });
      });

      pyshell.on('error', (err) => {
        console.error(`[${app.name}] Fatal Error: ${err}`);
        this.processes[appId].status = 'error';
        this.emit('app-init-error', { id: appId, error: err.toString() });
      });

      pyshell.on('close', (code) => {
        console.log(`[${app.name}] Initialization process closed with code ${code}`);
        
        // If exit code is 0 (success)
        if (code === 0) {
          this.processes[appId].status = 'initialized';
          this.emit('app-initialized', { id: appId, message: 'Initialization complete' });
        } else {
          this.processes[appId].status = 'error';
          this.emit('app-init-error', { id: appId, error: `Process exited with code ${code}` });
        }
      });

      return true;
    } catch (error) {
      console.error(`Failed to initialize ${app.name}: ${error}`);
      this.emit('app-init-error', { id: appId, error: error.toString() });
      return false;
    }
  }

  // Launch a specific app
  launchApp(appId) {
    const app = this.apps.find(a => a.id === appId);
    if (!app) {
      this.emit('app-launch-error', { id: appId, error: 'App not found' });
      return false;
    }

    try {
      // Terminate any existing processes for this app
      this.terminateApp(appId);

      // Configure PythonShell options
      const options = {
        mode: 'text',
        pythonPath: app.pythonPath || 'python',
        pythonOptions: ['-u'], // Unbuffered output
        scriptPath: app.scriptPath,
        args: app.launchArgs || []
      };

      // Start app process
      const pyshell = new PythonShell(app.mainScript, options);
      this.processes[appId] = {
        process: pyshell,
        status: 'running',
        type: 'main'
      };

      // Handle process events
      pyshell.on('message', (message) => {
        this.emit('app-message', { id: appId, message, type: 'main' });
      });

      pyshell.on('stderr', (err) => {
        console.error(`[${app.name}] Error: ${err}`);
        this.emit('app-error', { id: appId, error: err, type: 'main' });
      });

      pyshell.on('error', (err) => {
        console.error(`[${app.name}] Fatal Error: ${err}`);
        this.processes[appId].status = 'error';
        this.emit('app-launch-error', { id: appId, error: err.toString() });
      });

      pyshell.on('close', (code) => {
        console.log(`[${app.name}] Process closed with code ${code}`);
        delete this.processes[appId];
        this.emit('app-closed', { id: appId, code });
      });

      this.emit('app-launched', { id: appId });
      return true;
    } catch (error) {
      console.error(`Failed to launch ${app.name}: ${error}`);
      this.emit('app-launch-error', { id: appId, error: error.toString() });
      return false;
    }
  }

  // Terminate a specific app
  terminateApp(appId) {
    if (this.processes[appId] && this.processes[appId].process) {
      try {
        this.processes[appId].process.terminate();
        delete this.processes[appId];
        this.emit('app-terminated', { id: appId });
        return true;
      } catch (error) {
        console.error(`Failed to terminate app ${appId}: ${error}`);
        this.emit('app-terminate-error', { id: appId, error: error.toString() });
        return false;
      }
    }
    return false;
  }

  // Terminate all processes
  terminateAllApps() {
    Object.keys(this.processes).forEach(appId => {
      this.terminateApp(appId);
    });
  }

  // Get the status of all apps
  getAppStatuses() {
    const statuses = {};
    this.apps.forEach(app => {
      if (this.processes[app.id]) {
        statuses[app.id] = this.processes[app.id].status;
      } else {
        statuses[app.id] = 'idle';
      }
    });
    return statuses;
  }

  // Get the status of a specific app
  getAppStatus(appId) {
    if (this.processes[appId]) {
      return this.processes[appId].status;
    }
    return 'idle';
  }
}

module.exports = AppManager;