// Renderer.js - Handles UI interactions for CLEM Advanced UI

// DOM Elements
const loadingIndicator = document.getElementById('loadingIndicator');
const initProgressBar = document.getElementById('initProgressBar');
const statusMessages = document.getElementById('statusMessages');
const systemStatus = document.getElementById('systemStatus');
const cpuStatus = document.getElementById('cpuStatus');
const memoryStatus = document.getElementById('memoryStatus');
const notificationArea = document.getElementById('notificationArea');
const featureViewer = document.getElementById('featureViewer');
const featureContent = document.getElementById('featureContent');
const featureTitle = document.getElementById('featureTitle');
const recentActivitiesList = document.getElementById('recentActivitiesList');
const systemStatusValue = document.getElementById('systemStatusValue');
const modelsLoadedValue = document.getElementById('modelsLoadedValue');
const cameraStatusValue = document.getElementById('cameraStatusValue');

// Control buttons
const minimizeBtn = document.getElementById('minimizeBtn');
const maximizeBtn = document.getElementById('maximizeBtn');
const closeBtn = document.getElementById('closeBtn');
const closeFeatureBtn = document.getElementById('closeFeatureBtn');
const navItems = document.querySelectorAll('.nav-item');
const actionButtons = document.querySelectorAll('.action-btn');
const featureButtons = document.querySelectorAll('.feature-btn');

// Templates
const toastTemplate = document.getElementById('toastTemplate');

// App state
let apps = [];
let activeSection = 'dashboard';
let activeFeature = null;
let appInitCount = 0;

// Initialize the UI
async function initializeUI() {
  try {
    // Retrieve apps from the main process
    apps = await window.electronAPI.getApps();
    
    // If we have apps, update progress bar to reflect initialization process
    if (apps.length > 0) {
      // Set initial progress to 5%
      initProgressBar.style.width = '5%';
      addStatusMessage('Starting initialization of features...');
      
      // Update models loaded counter
      modelsLoadedValue.textContent = `${apps.length} available`;
      
      // Immediately after getting apps, update progress to 10%
      setTimeout(() => {
        initProgressBar.style.width = '10%';
      }, 200);
      
      // Set up navigation and section switching
      setupNavigationEvents();
      
      // Create recent activities
      populateRecentActivities();
      
      // Load app icons
      loadAppIcons();
      
      // Setup feature activation buttons
      setupFeatureButtons();
      
      // Update progress to 20%
      setTimeout(() => {
        initProgressBar.style.width = '20%';
        addStatusMessage('Initializing AI models...');
      }, 500);
      
      // Set up event listeners for real-time updates
      setupEventListeners();
      
      // Update progress to 30% to show initialization is progressing
      setTimeout(() => {
        initProgressBar.style.width = '30%';
        addStatusMessage('Setting up feature services...');
      }, 800);
      
      // Force additional progress updates to provide visual feedback
      setTimeout(() => {
        initProgressBar.style.width = '40%';
        addStatusMessage('Configuring computer vision modules...');
      }, 1500);
      
      setTimeout(() => {
        initProgressBar.style.width = '50%';
        addStatusMessage('Starting gesture recognition system...');
      }, 2500);
      
      // Check device capabilities
      checkDeviceCapabilities();
    } else {
      showToast('Error', 'No applications found in configuration.', 'error');
      hideLoading();
    }
  } catch (error) {
    console.error('Failed to initialize UI:', error);
    showToast('Error', 'Failed to initialize system.', 'error');
    hideLoading();
  }
}

// Check device capabilities like camera
function checkDeviceCapabilities() {
  addStatusMessage('Checking camera availability...');
  
  // Check if camera is available
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        cameraStatusValue.textContent = 'Available';
        addStatusMessage('Camera is available and functioning');
        stream.getTracks().forEach(track => track.stop());
        
        // Update progress to 70%
        initProgressBar.style.width = '70%';
        addStatusMessage('Hardware check complete');
        
        // Continue with initialization
        setTimeout(() => {
          initProgressBar.style.width = '100%';
          addStatusMessage('System initialization complete');
          setTimeout(hideLoading, 800);
        }, 1000);
      })
      .catch(err => {
        console.log('Camera not available: ', err);
        cameraStatusValue.textContent = 'Unavailable';
        addStatusMessage('Camera is not available, some features may be limited', 'warning');
        
        // Still complete progress
        initProgressBar.style.width = '100%';
        addStatusMessage('System initialization complete with warnings');
        setTimeout(hideLoading, 800);
      });
  } else {
    cameraStatusValue.textContent = 'Not Supported';
    addStatusMessage('Camera API not supported, some features may be limited', 'warning');
    
    // Still complete progress
    initProgressBar.style.width = '100%';
    addStatusMessage('System initialization complete with warnings');
    setTimeout(hideLoading, 800);
  }
}

// Set up navigation between sections
function setupNavigationEvents() {
  navItems.forEach(navItem => {
    navItem.addEventListener('click', () => {
      const targetSection = navItem.getAttribute('data-section');
      switchSection(targetSection);
    });
  });
}

// Switch between content sections
function switchSection(sectionId) {
  // Update nav active state
  navItems.forEach(navItem => {
    if (navItem.getAttribute('data-section') === sectionId) {
      navItem.classList.add('active');
    } else {
      navItem.classList.remove('active');
    }
  });
  
  // Hide all sections
  const sections = document.querySelectorAll('.content-section');
  sections.forEach(section => section.classList.remove('active'));
  
  // Show target section
  const targetSection = document.getElementById(`${sectionId}-section`);
  if (targetSection) {
    targetSection.classList.add('active');
    activeSection = sectionId;
  }
}

// Setup feature buttons
function setupFeatureButtons() {
  // Quick action buttons
  actionButtons.forEach(button => {
    const featureId = button.getAttribute('data-feature');
    button.addEventListener('click', () => activateFeature(featureId));
  });
  
  // Feature card buttons
  const featureCards = document.querySelectorAll('.feature-card');
  featureCards.forEach(card => {
    const featureId = card.getAttribute('data-feature');
    
    // The whole card can be clicked
    card.addEventListener('click', (e) => {
      // Don't activate if clicking the button itself (it will handle its own click)
      if (!e.target.classList.contains('feature-btn') && 
          !e.target.closest('.feature-btn')) {
        activateFeature(featureId);
      }
    });
    
    // Button specific click
    const button = card.querySelector('.feature-btn');
    if (button) {
      button.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent card click
        activateFeature(featureId);
      });
    }
  });
}

// Activate a specific feature
async function activateFeature(featureId) {
  if (!featureId) return;
  
  const app = apps.find(a => a.id === featureId);
  if (!app) {
    showToast('Error', 'Feature not found', 'error');
    return;
  }
  
  // Set active feature
  activeFeature = featureId;
  
  // Show the feature viewer
  featureTitle.textContent = app.name;
  featureViewer.classList.add('active');
  
  // Add loading state to feature content
  featureContent.innerHTML = `
    <div class="feature-loading">
      <div class="futuristic-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      <div class="spinner-text">Initializing ${app.name}...</div>
    </div>
  `;
  
  // Add to recent activities
  addRecentActivity(app.name, app.id);
  
  try {
    showToast('Activating', `Starting ${app.name}...`, 'info');
    const success = await window.electronAPI.launchApp(featureId);
    
    if (success) {
      showToast('Success', `${app.name} activated successfully.`, 'success');
      
      // Create feature content container
      const contentContainer = document.createElement('div');
      contentContainer.className = 'feature-content-container';
      
      // For features that might have a video feed, create a video area
      if (['face-reco', 'emotions', 'analyse', 'SignLang', 'item-detection', 'air-writing', 'media-control'].includes(featureId)) {
        contentContainer.innerHTML = `
          <div class="feature-video-area">
            <div class="video-placeholder">
              <i class="fas fa-camera"></i>
              <p>Camera feed will display here</p>
              <p class="small-text">(Actual feed will be shown when Python app connects)</p>
            </div>
          </div>
          <div class="feature-controls">
            <div class="feature-stats">
              <div class="stat-item">
                <span class="stat-label">Status:</span>
                <span class="stat-value">Running</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Detection:</span>
                <span class="stat-value">Ready</span>
              </div>
            </div>
            <div class="feature-actions">
              <button class="feature-action-btn pause-btn">
                <i class="fas fa-pause"></i>
                <span>Pause</span>
              </button>
              <button class="feature-action-btn settings-btn">
                <i class="fas fa-cog"></i>
                <span>Settings</span>
              </button>
              <button class="feature-action-btn fullscreen-btn">
                <i class="fas fa-expand"></i>
                <span>Fullscreen</span>
              </button>
            </div>
          </div>
        `;
      } 
      // For download apps, create a form interface
      else if (['youtube-download', 'music-download'].includes(featureId)) {
        contentContainer.innerHTML = `
          <div class="feature-form">
            <h3>Enter URL to download</h3>
            <div class="form-group">
              <input type="text" class="form-control" placeholder="Enter URL here...">
              <button class="form-btn">Start Download</button>
            </div>
            <div class="download-options">
              <div class="option-group">
                <label>Quality:</label>
                <select class="quality-select">
                  <option value="highest">Highest</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div class="option-group">
                <label>Format:</label>
                <select class="format-select">
                  <option value="auto">Auto</option>
                  <option value="mp4">MP4</option>
                  <option value="mp3">MP3 (audio only)</option>
                  <option value="webm">WebM</option>
                </select>
              </div>
            </div>
            <div class="download-status">
              <h4>Downloads</h4>
              <div class="download-list">
                <p class="no-downloads">No active downloads</p>
              </div>
            </div>
          </div>
        `;
      }
      // For phone info, create a connection interface
      else if (featureId === 'phone-info') {
        contentContainer.innerHTML = `
          <div class="feature-form">
            <h3>Phone Connection</h3>
            <div class="connection-status">
              <i class="fas fa-mobile-alt"></i>
              <p>No device connected</p>
            </div>
            <div class="connection-options">
              <button class="connection-btn">
                <i class="fas fa-link"></i>
                <span>Connect Device</span>
              </button>
              <button class="connection-btn disabled">
                <i class="fas fa-info-circle"></i>
                <span>View Device Info</span>
              </button>
              <button class="connection-btn disabled">
                <i class="fas fa-file-export"></i>
                <span>Export Data</span>
              </button>
            </div>
          </div>
        `;
      }
      // For health report, create a reports interface
      else if (featureId === 'health-report') {
        contentContainer.innerHTML = `
          <div class="feature-reports">
            <div class="reports-header">
              <h3>Health Analysis Reports</h3>
              <div class="report-filters">
                <button class="report-filter active">All</button>
                <button class="report-filter">Last Week</button>
                <button class="report-filter">Last Month</button>
              </div>
            </div>
            <div class="reports-list">
              <div class="report-item">
                <div class="report-icon">
                  <i class="fas fa-heartbeat"></i>
                </div>
                <div class="report-info">
                  <h4>Full Health Analysis</h4>
                  <p>April 28, 2025</p>
                </div>
                <button class="report-view-btn">View</button>
              </div>
              <div class="report-item">
                <div class="report-icon">
                  <i class="fas fa-eye"></i>
                </div>
                <div class="report-info">
                  <h4>Eye Tracking Analysis</h4>
                  <p>April 25, 2025</p>
                </div>
                <button class="report-view-btn">View</button>
              </div>
              <div class="report-item">
                <div class="report-icon">
                  <i class="fas fa-smile"></i>
                </div>
                <div class="report-info">
                  <h4>Facial Symmetry Report</h4>
                  <p>April 22, 2025</p>
                </div>
                <button class="report-view-btn">View</button>
              </div>
            </div>
          </div>
        `;
      }
      
      // Replace loading with content
      featureContent.innerHTML = '';
      featureContent.appendChild(contentContainer);
      
      // Add event listeners for feature-specific actions
      setupFeatureContentEvents(featureId);
    } else {
      showToast('Error', 'Failed to activate feature.', 'error');
      featureContent.innerHTML = `
        <div class="feature-error">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>Failed to activate feature</h3>
          <p>There was an error starting ${app.name}. Please check logs or try again.</p>
          <button class="retry-btn">Try Again</button>
        </div>
      `;
      
      // Add retry button event listener
      const retryBtn = featureContent.querySelector('.retry-btn');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          activateFeature(featureId);
        });
      }
    }
  } catch (error) {
    console.error('Error activating feature:', error);
    showToast('Error', `Failed to activate: ${error.message}`, 'error');
    
    featureContent.innerHTML = `
      <div class="feature-error">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error</h3>
        <p>${error.message}</p>
        <button class="retry-btn">Try Again</button>
      </div>
    `;
  }
}

// Setup events for feature content
function setupFeatureContentEvents(featureId) {
  // Video feature buttons
  const pauseBtn = featureContent.querySelector('.pause-btn');
  const settingsBtn = featureContent.querySelector('.settings-btn');
  const fullscreenBtn = featureContent.querySelector('.fullscreen-btn');
  
  if (pauseBtn) {
    pauseBtn.addEventListener('click', () => {
      if (pauseBtn.classList.contains('paused')) {
        pauseBtn.classList.remove('paused');
        pauseBtn.innerHTML = `<i class="fas fa-pause"></i><span>Pause</span>`;
        showToast('Resumed', `${apps.find(a => a.id === featureId).name} resumed`, 'info');
      } else {
        pauseBtn.classList.add('paused');
        pauseBtn.innerHTML = `<i class="fas fa-play"></i><span>Resume</span>`;
        showToast('Paused', `${apps.find(a => a.id === featureId).name} paused`, 'info');
      }
    });
  }
  
  if (settingsBtn) {
    settingsBtn.addEventListener('click', () => {
      showToast('Settings', 'Feature settings dialog would appear here', 'info');
    });
  }
  
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      if (document.fullscreenElement) {
        document.exitFullscreen();
        fullscreenBtn.innerHTML = `<i class="fas fa-expand"></i><span>Fullscreen</span>`;
      } else {
        featureViewer.requestFullscreen();
        fullscreenBtn.innerHTML = `<i class="fas fa-compress"></i><span>Exit Fullscreen</span>`;
      }
    });
  }
  
  // For download features
  const formBtn = featureContent.querySelector('.form-btn');
  if (formBtn) {
    formBtn.addEventListener('click', () => {
      const input = featureContent.querySelector('.form-control');
      if (input && input.value.trim()) {
        showToast('Download', `Started download process for ${input.value}`, 'info');
        
        // Show a download entry
        const downloadList = featureContent.querySelector('.download-list');
        if (downloadList) {
          downloadList.querySelector('.no-downloads')?.remove();
          
          const downloadItem = document.createElement('div');
          downloadItem.className = 'download-item';
          downloadItem.innerHTML = `
            <div class="download-info">
              <p class="download-name">${input.value.split('/').pop() || 'File'}</p>
              <div class="download-progress">
                <div class="progress-bar" style="width: 0%"></div>
              </div>
              <p class="download-status">Initializing...</p>
            </div>
            <button class="download-cancel-btn">
              <i class="fas fa-times"></i>
            </button>
          `;
          
          downloadList.appendChild(downloadItem);
          
          // Simulate progress
          let progress = 0;
          const progressBar = downloadItem.querySelector('.progress-bar');
          const statusText = downloadItem.querySelector('.download-status');
          
          const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 100) progress = 100;
            
            progressBar.style.width = `${progress}%`;
            
            if (progress < 100) {
              statusText.textContent = `Downloading... ${Math.floor(progress)}%`;
            } else {
              statusText.textContent = 'Complete';
              clearInterval(interval);
            }
          }, 500);
          
          // Cancel button
          downloadItem.querySelector('.download-cancel-btn').addEventListener('click', () => {
            clearInterval(interval);
            downloadItem.remove();
            showToast('Cancelled', 'Download cancelled', 'warning');
            
            // Show "no downloads" message if this was the last one
            if (downloadList.children.length === 0) {
              const noDownloads = document.createElement('p');
              noDownloads.className = 'no-downloads';
              noDownloads.textContent = 'No active downloads';
              downloadList.appendChild(noDownloads);
            }
          });
        }
      }
    });
  }
  
  // For phone info connection
  const connectionBtn = featureContent.querySelector('.connection-btn');
  if (connectionBtn) {
    connectionBtn.addEventListener('click', () => {
      const connectionStatus = featureContent.querySelector('.connection-status');
      if (connectionStatus) {
        connectionStatus.innerHTML = `
          <i class="fas fa-spinner fa-spin"></i>
          <p>Searching for devices...</p>
        `;
        
        setTimeout(() => {
          connectionStatus.innerHTML = `
            <i class="fas fa-mobile-alt connected"></i>
            <p>Device connected: Pixel 7</p>
            <div class="device-details">
              <p><strong>Model:</strong> Google Pixel 7</p>
              <p><strong>OS:</strong> Android 14</p>
              <p><strong>Storage:</strong> 128GB (45% used)</p>
            </div>
          `;
          
          // Enable buttons
          const buttons = featureContent.querySelectorAll('.connection-btn.disabled');
          buttons.forEach(btn => btn.classList.remove('disabled'));
          
          showToast('Connected', 'Phone connected successfully', 'success');
        }, 2000);
      }
    });
  }
  
  // For health report view buttons
  const reportViewBtns = featureContent.querySelectorAll('.report-view-btn');
  if (reportViewBtns.length) {
    reportViewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const reportTitle = btn.closest('.report-item').querySelector('h4').textContent;
        showToast('Report', `Opening ${reportTitle}`, 'info');
      });
    });
  }
}

// Close current active feature
function closeFeature() {
  if (!activeFeature) return;
  
  featureViewer.classList.remove('active');
  
  // Terminate the Python process
  window.electronAPI.terminateApp(activeFeature).then(() => {
    const app = apps.find(a => a.id === activeFeature);
    if (app) {
      showToast('Closed', `${app.name} has been deactivated.`, 'info');
    }
    
    activeFeature = null;
  });
}

// Add an entry to recent activities
function addRecentActivity(name, id) {
  // Create activity item
  const activityItem = document.createElement('div');
  activityItem.className = 'activity-item';
  
  // Get icon based on id
  let icon = 'fa-cube';
  if (id.includes('face') || id === 'analyse') icon = 'fa-user';
  if (id === 'emotions') icon = 'fa-smile';
  if (id === 'SignLang') icon = 'fa-sign-language';
  if (id === 'media-control') icon = 'fa-music';
  if (id === 'item-detection') icon = 'fa-box';
  if (id.includes('download')) icon = 'fa-download';
  if (id === 'phone-info') icon = 'fa-mobile-alt';
  if (id === 'air-writing') icon = 'fa-pencil-alt';
  
  // Create timestamp
  const now = new Date();
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  
  // Populate activity item
  activityItem.innerHTML = `
    <div class="activity-icon">
      <i class="fas ${icon}"></i>
    </div>
    <div class="activity-details">
      <div class="activity-title">${name} activated</div>
      <div class="activity-time">${timeStr}</div>
    </div>
  `;
  
  // Add to list (prepend)
  if (recentActivitiesList) {
    recentActivitiesList.insertBefore(activityItem, recentActivitiesList.firstChild);
    
    // Limit to 5 items
    while (recentActivitiesList.children.length > 5) {
      recentActivitiesList.removeChild(recentActivitiesList.lastChild);
    }
  }
}

// Populate initial recent activities
function populateRecentActivities() {
  // Add some dummy recent activities to start with
  const dummyActivities = [
    { name: 'System', activity: 'started', time: 'Today' },
    { name: 'Face Recognition', activity: 'trained new model', time: 'Yesterday' },
    { name: 'ASL Translator', activity: 'updated dictionary', time: 'Apr 28' }
  ];
  
  if (recentActivitiesList) {
    recentActivitiesList.innerHTML = '';
    
    dummyActivities.forEach(activity => {
      const activityItem = document.createElement('div');
      activityItem.className = 'activity-item';
      
      // Get appropriate icon
      let icon = 'fa-cube';
      if (activity.name === 'Face Recognition') icon = 'fa-user';
      if (activity.name === 'ASL Translator') icon = 'fa-sign-language';
      if (activity.name === 'System') icon = 'fa-microchip';
      
      activityItem.innerHTML = `
        <div class="activity-icon">
          <i class="fas ${icon}"></i>
        </div>
        <div class="activity-details">
          <div class="activity-title">${activity.name} ${activity.activity}</div>
          <div class="activity-time">${activity.time}</div>
        </div>
      `;
      
      recentActivitiesList.appendChild(activityItem);
    });
  }
}

// Add status message
function addStatusMessage(message, type = 'info') {
  if (!statusMessages) return;
  
  const messageElement = document.createElement('div');
  messageElement.className = `status-message ${type}`;
  messageElement.textContent = message;
  
  statusMessages.appendChild(messageElement);
  statusMessages.scrollTop = statusMessages.scrollHeight;
}

// Show toast notification
function showToast(title, message, type = 'info') {
  if (!toastTemplate || !notificationArea) return;
  
  const toastClone = toastTemplate.content.cloneNode(true);
  const toast = toastClone.querySelector('.toast-notification');
  
  toast.classList.add(type);
  toast.querySelector('.toast-title').textContent = title;
  toast.querySelector('.toast-message').textContent = message;
  
  // Set icon based on type
  const icon = document.createElement('i');
  switch (type) {
    case 'success':
      icon.className = 'fas fa-check-circle';
      icon.style.color = 'var(--success-color)';
      break;
    case 'warning':
      icon.className = 'fas fa-exclamation-triangle';
      icon.style.color = 'var(--warning-color)';
      break;
    case 'error':
      icon.className = 'fas fa-times-circle';
      icon.style.color = 'var(--error-color)';
      break;
    default:
      icon.className = 'fas fa-info-circle';
      icon.style.color = 'var(--primary-color)';
  }
  
  toast.querySelector('.toast-icon').appendChild(icon);
  
  // Add close button event
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.classList.add('sliding-out');
    setTimeout(() => {
      toast.remove();
    }, 300);
  });
  
  // Auto-remove after 5 seconds
  notificationArea.appendChild(toast);
  setTimeout(() => {
    if (toast.parentNode) {
      toast.classList.add('sliding-out');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.remove();
        }
      }, 300);
    }
  }, 5000);
}

// Hide loading indicator
function hideLoading() {
  if (!loadingIndicator) return;
  
  loadingIndicator.classList.add('hidden');
  systemStatus.textContent = 'All systems operational';
  systemStatusValue.textContent = 'Operational';
  
  showToast('Ready', 'CLEM system is initialized and ready.', 'success');
  
  // Start system resource monitoring
  startResourceMonitoring();
}

// Simulate system resource monitoring
function startResourceMonitoring() {
  // Update CPU and memory usage periodically
  setInterval(() => {
    // Simulate CPU usage between 1-8%
    const cpuUsage = Math.floor(Math.random() * 8) + 1;
    cpuStatus.textContent = `CPU: ${cpuUsage}%`;
    
    // Simulate memory usage between 450-550MB
    const memoryUsage = Math.floor(Math.random() * 100) + 450;
    memoryStatus.textContent = `Memory: ${memoryUsage}MB`;
  }, 5000);
}

// Set up event listeners
function setupEventListeners() {
  // Window controls
  minimizeBtn.addEventListener('click', () => window.electronAPI.minimizeApp());
  maximizeBtn.addEventListener('click', () => window.electronAPI.maximizeApp());
  closeBtn.addEventListener('click', () => window.electronAPI.closeApp());
  
  // Close feature button
  closeFeatureBtn.addEventListener('click', closeFeature);
  
  // App status updates
  window.electronAPI.onAppStatusUpdate((data) => {
    updateAppStatus(data.id, data.status, data.message);
  });
  
  // Force completion of initialization after a timeout if apps are stuck
  setTimeout(() => {
    if (loadingIndicator && !loadingIndicator.classList.contains('hidden')) {
      hideLoading();
    }
  }, 20000); // 20 second timeout
  
  // All apps initialized event
  window.electronAPI.onAllAppsInitialized(() => {
    console.log("All apps initialized event received");
    hideLoading();
  });
  
  // App launch events
  window.electronAPI.onAppLaunched((data) => {
    const app = apps.find(a => a.id === data.id);
    if (app) {
      showToast('Activated', `${app.name} is now active.`, 'success');
    }
  });
  
  window.electronAPI.onAppLaunchError((data) => {
    const app = apps.find(a => a.id === data.id);
    if (app) {
      showToast('Error', `Failed to activate ${app.name}: ${data.error}`, 'error');
    }
  });
  
  window.electronAPI.onAppClosed((data) => {
    const app = apps.find(a => a.id === data.id);
    if (app) {
      showToast('Closed', `${app.name} has been closed.`, 'info');
    }
  });
  
  // Settings toggles
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('change', () => {
      showToast('Settings', 'Dark mode setting saved', 'info');
    });
  }
  
  const notificationsToggle = document.getElementById('notificationsToggle');
  if (notificationsToggle) {
    notificationsToggle.addEventListener('change', () => {
      showToast('Settings', 'Notification settings saved', 'info');
    });
  }
  
  // Camera and model settings
  const cameraSelect = document.getElementById('cameraSelect');
  if (cameraSelect) {
    cameraSelect.addEventListener('change', () => {
      showToast('Settings', 'Camera source updated', 'info');
    });
  }
  
  const modelPrecisionSelect = document.getElementById('modelPrecisionSelect');
  if (modelPrecisionSelect) {
    modelPrecisionSelect.addEventListener('change', () => {
      showToast('Settings', 'AI model precision updated', 'info');
    });
  }
  
  // Handle fullscreen change
  document.addEventListener('fullscreenchange', () => {
    const fullscreenBtn = document.querySelector('.fullscreen-btn');
    if (fullscreenBtn) {
      if (document.fullscreenElement) {
        fullscreenBtn.innerHTML = `<i class="fas fa-compress"></i><span>Exit Fullscreen</span>`;
      } else {
        fullscreenBtn.innerHTML = `<i class="fas fa-expand"></i><span>Fullscreen</span>`;
      }
    }
  });
}

// Update app status
function updateAppStatus(appId, status, message) {
  // If this is the currently active feature, update its status
  if (activeFeature === appId) {
    const statusValue = featureContent.querySelector('.stat-value');
    if (statusValue) {
      if (status === 'initialized') {
        statusValue.textContent = 'Running';
      } else if (status === 'error') {
        statusValue.textContent = 'Error';
      }
    }
  }
  
  // Count initialized apps
  if (status === 'initialized') {
    appInitCount++;
    
    // Add status message
    const app = apps.find(a => a.id === appId);
    addStatusMessage(`${app.name} initialized successfully.`);
  } else if (status === 'error') {
    // Add status message
    const app = apps.find(a => a.id === appId);
    addStatusMessage(`Error initializing ${app.name}: ${message}`, 'error');
  }
}

// Add some animation to the grid background
function animateGrid() {
  const grid = document.querySelector('.grid');
  if (!grid) return;
  
  let offset = 0;
  
  setInterval(() => {
    offset += 0.5;
    grid.style.backgroundPosition = `0px ${offset}px`;
  }, 50);
}

// Load app icons for feature cards and buttons
function loadAppIcons() {
  // Update feature cards with app icons
  const featureCards = document.querySelectorAll('.feature-card');
  featureCards.forEach(card => {
    const featureId = card.getAttribute('data-feature');
    const app = apps.find(a => a.id === featureId);
    
    if (app && app.icon) {
      // Replace FontAwesome icon with app icon
      const iconContainer = card.querySelector('.feature-icon');
      if (iconContainer) {
        // Clear existing content
        iconContainer.innerHTML = '';
        
        // Create image element
        const iconImg = document.createElement('img');
        iconImg.src = app.icon;
        iconImg.alt = `${app.name} icon`;
        iconImg.className = 'app-icon';
        
        // Add to container
        iconContainer.appendChild(iconImg);
      }
    }
  });
  
  // Update quick action buttons with app icons
  const actionButtons = document.querySelectorAll('.action-btn');
  actionButtons.forEach(button => {
    const featureId = button.getAttribute('data-feature');
    const app = apps.find(a => a.id === featureId);
    
    if (app && app.icon) {
      // Replace FontAwesome icon with app icon
      const iconElement = button.querySelector('i');
      if (iconElement) {
        // Create image element to replace the Font Awesome icon
        const iconImg = document.createElement('img');
        iconImg.src = app.icon;
        iconImg.alt = `${app.name} icon`;
        iconImg.className = 'action-icon';
        
        // Replace icon with image
        iconElement.replaceWith(iconImg);
      }
    }
  });
  
  addStatusMessage('App icons loaded successfully');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  animateGrid();
  initializeUI();
});