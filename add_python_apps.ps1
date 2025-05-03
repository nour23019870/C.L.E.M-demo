$pythonAppsDir = "python-apps"

# Get all subdirectories in python-apps
$appDirs = Get-ChildItem -Path $pythonAppsDir -Directory

# Loop through each app directory
foreach ($appDir in $appDirs) {
    $appPath = $appDir.FullName
    
    # Add Python files
    $pythonFiles = Get-ChildItem -Path $appPath -Include "*.py" -Recurse -File | Where-Object { $_.FullName -notlike "*\env\*" }
    foreach ($file in $pythonFiles) {
        git add -f $file.FullName
    }
    
    # Add documentation and configuration files
    $docFiles = Get-ChildItem -Path $appPath -Include "*.md", "*.txt", "*.docx", "*.json" -Recurse -File | Where-Object { $_.FullName -notlike "*\env\*" }
    foreach ($file in $docFiles) {
        git add -f $file.FullName
    }
    
    # Add model files
    $modelFiles = Get-ChildItem -Path $appPath -Include "*.h5", "*.pt", "*.pth", "*.model", "*.caffemodel", "*.t7", "*.weights", "*.onnx", "*.pb", "*.pbtxt", "*.prototxt" -Recurse -File | Where-Object { $_.FullName -notlike "*\env\*" }
    foreach ($file in $modelFiles) {
        git add -f $file.FullName
    }
    
    # Add binary files
    $binaryFiles = Get-ChildItem -Path $appPath -Include "*.dll", "*.so", "*.pyd" -Recurse -File | Where-Object { $_.FullName -notlike "*\env\*" }
    foreach ($file in $binaryFiles) {
        git add -f $file.FullName
    }
    
    # Add image and other media files
    $mediaFiles = Get-ChildItem -Path $appPath -Include "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.mp3", "*.mp4", "*.wav" -Recurse -File | Where-Object { $_.FullName -notlike "*\env\*" }
    foreach ($file in $mediaFiles) {
        git add -f $file.FullName
    }
}

# Check what was added
Write-Host "Files added to git staging area. Run 'git status' to see them."