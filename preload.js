const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to communicate with
// the main process via IPC
contextBridge.exposeInMainWorld('electronAPI', {
  // App management
  getApps: () => ipcRenderer.invoke('get-apps'),
  launchApp: (appId) => ipcRenderer.invoke('launch-app', appId),
  terminateApp: (appId) => ipcRenderer.invoke('terminate-app', appId),
  
  // Window control
  closeApp: () => ipcRenderer.invoke('close-app'),
  minimizeApp: () => ipcRenderer.invoke('minimize-app'),
  maximizeApp: () => ipcRenderer.invoke('maximize-app'),
  
  // Event subscriptions
  onAppStatusUpdate: (callback) => 
    ipcRenderer.on('app-status-update', (_, data) => callback(data)),
  onAppLaunched: (callback) => 
    ipcRenderer.on('app-launched', (_, data) => callback(data)),
  onAppLaunchError: (callback) => 
    ipcRenderer.on('app-launch-error', (_, data) => callback(data)),
  onAppClosed: (callback) => 
    ipcRenderer.on('app-closed', (_, data) => callback(data)),
  onAllAppsInitialized: (callback) =>
    ipcRenderer.on('all-apps-initialized', () => callback()),
    
  // Remove event listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});