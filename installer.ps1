# Get the current working directory
$CurrentDirectory = (Get-Location).Path

# Check if we are currently running with administrative privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # Create a new process object that starts PowerShell with elevated privileges
    $newProcess = New-Object System.Diagnostics.ProcessStartInfo "PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path

    # Ensure the path is properly escaped
    $escapedScriptPath = $scriptPath -replace '\\', '\\\\' -replace '"', '\"'

    # Specify the current script path and name as a parameter with a cd command
    $newProcess.Arguments = "-NoExit -Command `"cd '$CurrentDirectory'; & '$escapedScriptPath'`""

    # Set the working directory of the new process to be the current directory
    $newProcess.WorkingDirectory = $CurrentDirectory

    # Indicate that the process should be elevated
    $newProcess.Verb = "runas"

    # Start the new process
    [System.Diagnostics.Process]::Start($newProcess)

    # Exit from the current, unelevated, process
    exit
}

# Now running with admin privileges
$logFile = "$CurrentDirectory\install.log"

Add-Content -Path $logFile -Value "Log file created at $logFile"

$StartUpFolder = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs"

try {
    # Check if the OverwatchTime directory exists in the start up folder
    if (-not (Test-Path "$StartUpFolder\OverwatchTime")) {
        # Create new folder called OverwatchTime in the start up folder
        New-Item -Path $StartUpFolder -Name "OverwatchTime" -ItemType "directory" -ErrorAction Stop
        Add-Content -Path $logFile -Value "Directory created at $StartUpFolder\OverwatchTime"
    }

    # Check if the OverwatchTimeData directory exists in program data
    if (-not (Test-Path "$env:ProgramData\OverwatchTimeData")) {
        # Create a new folder in program data
        New-Item -Path $env:ProgramData -Name "OverwatchTimeData" -ItemType "directory" -ErrorAction Stop
        Add-Content -Path $logFile -Value "Directory created at $env:ProgramData\OverwatchTimeData"
    }

    # Check if version file exists and compare the version in OverwatchTimeData with the current version
    $versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"

    $localVersion = Get-Content .\version.txt
    $gitHubVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content

    if ($localVersion -ne $gitHubVersion) {
        Add-Content -Path $logFile -Value "Local version: $localVersion is different from GitHub version: $gitHubVersion"
        
        # Perform updates for the OverwatchTime application
        PerformApplicationUpdate

        # Update the installer script
        UpdateInstallerScript
    } else {
        Add-Content -Path $logFile -Value "Local version matches GitHub version. No action taken."
    }
    
} catch {
    Add-Content -Path $logFile -Value "An error occurred: $_"
    Add-Content -Path $logFile -Value "At line: $($_.InvocationInfo.ScriptLineNumber)"
    Add-Content -Path $logFile -Value "Stack Trace:`n$($_.Exception.StackTrace)"
} finally {
    # Wait for user to hit enter
    Read-Host -Prompt "Press Enter to continue"
}

function PerformApplicationUpdate {
    # Define the paths and URLs
    $repoUrl = "https://github.com/ElTragedy/OverwatchTime/archive/refs/heads/main.zip"
    $zipPath = "$env:ProgramData\OverwatchTimeData\OverwatchTime.zip"
    $tempFolder = "$env:ProgramData\OverwatchTimeData\temp"
    $extractPath = "$env:ProgramData\OverwatchTimeData\temp\OverwatchTime-main"
    $versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"
    $oldExePath = "$StartUpFolder\OverwatchTime\OverwatchTime.exe"
    
    try {
        # Create a new WebClient object
        $webClient = New-Object System.Net.WebClient

        # Download the ZIP file
        $webClient.DownloadFile($repoUrl, $zipPath)
        Add-Content -Path $logFile -Value "Downloaded update ZIP from $repoUrl to $zipPath"

        # Check for a temp folder, if exists, delete it, then create a new one
        if (Test-Path $tempFolder) {
            Remove-Item -Path $tempFolder -Recurse -Force
        }
        New-Item -Path $env:ProgramData\OverwatchTimeData -Name "temp" -ItemType "directory" -ErrorAction Stop

        # Extract the ZIP file
        Expand-Archive -Path $zipPath -DestinationPath $tempFolder -Force
        Add-Content -Path $logFile -Value "Extracted ZIP to $tempFolder"

        # Remove the ZIP file
        Remove-Item -Path $zipPath -Force

        # Replace the following files: version.txt, OverwatchTime.exe
        # Delete the old version.txt, if it exists
        if (Test-Path $versionFile) {
            Remove-Item -Path $versionFile -Force
        }

        # Move the new version.txt to the OverwatchTimeData folder
        Move-Item "$extractPath\version.txt" $versionFile -Force

        # Rename the old executable if it exists
        if (Test-Path $oldExePath) {
            Rename-Item -Path $oldExePath -NewName "OverwatchTime_old.exe" -Force
        }

        # Move the new executable to the folder, overwrite if it already exists
        Copy-Item "$extractPath\dist\OverwatchTime.exe" "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop
        Add-Content -Path $logFile -Value "Executable copied to $StartUpFolder\OverwatchTime"

        # Remove temporary files
        Remove-Item -Path $extractPath -Recurse -Force

    } catch {
        Add-Content -Path $logFile -Value "An error occurred during the application update: $_"
        Add-Content -Path $logFile -Value "At line: $($_.InvocationInfo.ScriptLineNumber)"
        Add-Content -Path $logFile -Value "Stack Trace:`n$($_.Exception.StackTrace)"
    }
}


function UpdateInstallerScript {
    # Check if the installer needs an update
    $installerPath = $MyInvocation.MyCommand.Path
    $installerVersionFile = "$env:ProgramData\OverwatchTimeData\installer_version.txt"
    $remoteInstallerVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/installer_version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content

    $localInstallerVersion = if (Test-Path $installerVersionFile) { Get-Content $installerVersionFile } else { "" }

    if ($localInstallerVersion -ne $remoteInstallerVersion) {
        Add-Content -Path $logFile -Value "Installer version: $localInstallerVersion is different from GitHub installer version: $remoteInstallerVersion"

        # Download the new installer script
        $installerUrl = "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/installer.ps1"
        $newInstallerPath = "$CurrentDirectory\installer_new.ps1"

        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($installerUrl, $newInstallerPath)

        # Rename the old installer script
        Rename-Item -Path $installerPath -NewName "installer_old.ps1" -Force

        # Move the new installer script to the current location
        Move-Item -Path $newInstallerPath -Destination $installerPath -Force

        # Update the local installer version file
        Set-Content -Path $installerVersionFile -Value $remoteInstallerVersion

        Add-Content -Path $logFile -Value "Installer script updated to version $remoteInstallerVersion"
    } else {
        Add-Content -Path $logFile -Value "Installer script is up to date."
    }
}

