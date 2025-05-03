# CLEM: Comprehensive Learning and Execution Manager

![CLEM Logo](assets/icons/logo.png)

## 🌟 Overview

CLEM (Comprehensive Learning and Execution Manager) is a futuristic launcher for Python applications that provides a unified interface for multiple artificial intelligence and computer vision tools. It integrates various functionalities like air writing, emotion detection, face recognition, and media control into a single, easy-to-use platform.

## ✨ Features

- **Unified Interface**: Access multiple Python applications from a single dashboard
- **Modular Design**: Easily add or remove Python applications
- **Isolated Environments**: Each application runs in its own Python virtual environment
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Resource Efficient**: Only loads resources when they're needed

### 📱 Included Applications

- **Air Writing**: Draw in the air using hand gestures captured by your webcam
- **Emotion Detection**: Analyze and detect emotions from facial expressions
- **Face Recognition**: Identify and verify faces from images or video
- **Media Control**: Control media playback using hand gestures
- **Item Detection**: Detect and classify objects in images and videos
- **Sign Language**: Recognize and interpret sign language gestures
- **YouTube Downloader**: Download videos from YouTube
- **Phone Info**: Extract information from phone numbers

## 🛠️ Installation

### Prerequisites

- **Node.js** (v14+)
- **Python 3.10** (Note: CLEM is specifically designed for Python 3.10)
- **Webcam** (Required for vision-based applications)

### Automatic Installation

Run the installer script which will set up all required environments and dependencies:

```bash
# On Windows
installer.bat

# On macOS/Linux
add '#! bin/bash' to the top of the installer.bat file
rename it or save it as : installer.sh
chmod +x installer.sh
./installer.sh
```

## 🚀 Usage

1. Launch CLEM:
   ```bash
   # On Windows
   main.bat
   
   # On macOS/Linux
   add '#! bin/bash' to the top of the CLEM.bat file
   rename or save the file as '.sh' : CLEM.sh
   chmod +x CLEM.sh
   ./CLEM.sh
   ```

2. From the main interface, select the application you want to run
3. Each application has its own instructions and controls
4. To close an application, follow its exit procedure or close its window

## 📂 Project Structure

```
CLEM/
├── assets/             # Icons, images, and frontend assets
├── config/             # Configuration files
├── python-apps/        # Python applications
│   ├── air-writing/    # Air writing application
│   ├── emotions/       # Emotion detection application
│   ├── face_reco/      # Face recognition application
│   └── ...             # Other applications
├── Python310/          # Local Python 3.10 installation
├── scripts/            # Helper scripts
├── styles/             # CSS styles
├── main.js             # Main Electron process
├── index.html          # Main application window
├── installer.bat       # Windows installer
└── main.bat            # Windows launcher
```

## 🧩 Adding New Applications

To add a new Python application to CLEM:

1. Create a folder for your application in the `python-apps` directory
2. Include a `main.py` file as the entry point
3. Add a `requirements.txt` file listing all dependencies
4. Create a `README.md` to document your application
5. Run the PowerShell script to register your application:
   ```powershell
   .\add_python_apps.ps1
   ```

## 🔧 Development

### Building From Source

```bash
# Install dependencies
npm install

# Run in development mode
npm run start-dev
```

### Creating an Executable

To create a standalone executable:

```bash
# Install nexe (if needed)
npm install --save-dev nexe@3.3.2

# Build executable
npm run create-exe
```

## 🔍 Troubleshooting

- **Application won't start**: Ensure Python 3.10 and all dependencies are installed correctly
- **Camera not working**: Check camera permissions and ensure no other application is using the camera
- **Python errors**: Verify that the correct version of Python (3.10) is being used

## 📄 License

[MIT License](LICENSE.txt)

## 👏 Acknowledgments

- All the amazing open-source libraries that made this project possible
- The community contributors and testers

---

© 2025 CLEM Project
