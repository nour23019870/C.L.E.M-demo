# This script removes submodule configurations for python-apps directories

# Step 1: Remove submodule entries from .git/config
$gitConfigPath = ".git/config"
if (Test-Path $gitConfigPath) {
    $configContent = Get-Content $gitConfigPath
    $newContent = $configContent | Where-Object { 
        -not ($_ -match '\[submodule "python-apps') -and 
        -not ($_ -match 'path = python-apps/') 
    }
    $newContent | Set-Content $gitConfigPath
    Write-Host "Cleaned submodule entries from .git/config"
}

# Step 2: Remove submodule entries from .gitmodules if it exists
$gitmodulesPath = ".gitmodules"
if (Test-Path $gitmodulesPath) {
    $modulesContent = Get-Content $gitmodulesPath
    $newModulesContent = $modulesContent | Where-Object { 
        -not ($_ -match '\[submodule "python-apps') -and 
        -not ($_ -match 'path = python-apps/') 
    }
    $newModulesContent | Set-Content $gitmodulesPath
    Write-Host "Cleaned submodule entries from .gitmodules"
}

# Step 3: Remove cached submodule entries
Get-ChildItem -Path "python-apps" -Directory | ForEach-Object {
    $submoduleName = "python-apps/$($_.Name)"
    git rm --cached $submoduleName 2>$null
    Write-Host "Removed cached entry for $submoduleName"
}

# Step 4: Remove .git/modules/python-apps directory
$modulesDir = ".git/modules/python-apps"
if (Test-Path $modulesDir) {
    Remove-Item -Recurse -Force $modulesDir
    Write-Host "Removed $modulesDir directory"
}

Write-Host "Submodule cleanup completed. Now you can add the python-apps files."