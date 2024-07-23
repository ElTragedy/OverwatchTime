- Author: Aaron Sierra

# Requirements

- python 3

# Directions

Install python 3 if you havent already.

Before running the script, run pythonInstall.ps1 to install the required python packages.
This is just a list of "pip install" commands.

You only need to run pythonInstall one per update to the script. If you run it
once, you should be good to go until the next update to the script.

To run the script, run the following command:
python .\SayreTimeScript.py

# How to add images

Import a png image in the images folder. The size does not matter, the program will
auto resize any image so long as it is a png.


# Command for my reference:
pyinstaller --onefile --icon=OverwatchTime.ico OverwatchTime.py
o

# old code in case break
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

  # check if 1. version file exists 2. version in OverwatchTimeData is different
  # from the current version. If so, download the new version from github using wget
  $versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"

  if (Test-Path $versionFile) {
    # Compare the version in the file to the current version
    $localVersion = Get-Content .\version.txt
        
    # wget https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt
    # and whatever is in content is the version
    $gitHubVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content

    if ($localVersion -ne $gitHubVersion) {
      Add-Content -Path $logFile -Value "Local version: $localVersion is different from GitHub version: $gitHubVersion"

      # Download the new version from github
      $repoUrl = "https://github.com/ElTragedy/OverwatchTime/archive/refs/heads/main.zip"

      # Define the path where you want to save the ZIP file
      $zipPath = "$env:ProgramData\OverwatchTimeData\OverwatchTime.zip"

      # Create a new WebClient object
      $webClient = New-Object System.Net.WebClient

      # Download the file
      $webClient.DownloadFile($repoUrl, $zipPath)

      # Use Invoke-WebRequest to download the ZIP file
      #Invoke-WebRequest -Uri $repoUrl -OutFile $zipPath

      # Check for a temp folder, if exists, delete it, then create a new one
      $tempFolder = "$env:ProgramData\OverwatchTimeData\temp"
      if (Test-Path $tempFolder) {
        Remove-Item -Path $tempFolder -Recurse -Force
      }
      # Create temp folder
      New-Item -Path $env:ProgramData\OverwatchTimeData -Name "temp" -ItemType "directory" -ErrorAction Stop

      # Define the path where you want to extract the ZIP file
      $extractPath = "$env:ProgramData\OverwatchTimeData\temp"

      # Use Expand-Archive to extract the ZIP file
      Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

      # Remove the ZIP file
      Remove-Item -Path $zipPath -Force

      # Replace the following files: version.txt, OverwatchTime.exe, and the images folder
            
      # Delete the old version.txt, if it exists
      if (Test-Path $versionFile) {
        Remove-Item -Path $versionFile -Force
      }

      # Move the new version.txt to the OverwatchTimeData folder
      Move-Item "$extractPath\OverwatchTime-main\version.txt" $versionFile -Force

      # Rename the old executable if it exists
      $oldExePath = "$StartUpFolder\OverwatchTime\OverwatchTime.exe"
      if (Test-Path $oldExePath) {
        Rename-Item -Path $oldExePath -NewName "OverwatchTime_old.exe" -Force
      }

      # Move the new executable to the folder, overwrite if it already exists
      Copy-Item "$extractPath\OverwatchTime-main\dist\OverwatchTime.exe" "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop
      Add-Content -Path $logFile -Value "Executable copied to $StartUpFolder\OverwatchTime"

      # Remove temporary files
      Remove-Item -Path $extractPath -Recurse -Force
    }
    else {
      Add-Content -Path $logFile -Value "Local version matches GitHub version. No action taken."
    }
  }

  # Move executable to folder we made, overwrite if it already exists
  Copy-Item .\dist\OverwatchTime.exe "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop
  Add-Content -Path $logFile -Value "Executable copied to $StartUpFolder\OverwatchTime"

  # Move everything else into the data folder, overwrite if they already exist
  #
  #Move-Item .\* "$env:ProgramData\OverwatchTimeData" -Force -ErrorAction Stop
  #Add-Content -Path $logFile -Value "Files moved to $env:ProgramData\OverwatchTimeData"

  # Add images if any images were added to github
  # 1st check if the images folder exists in the data folder
  # 2nd wget the images folder from github and compare differences

}
catch {
  Add-Content -Path $logFile -Value "An error occurred: $_"
  Add-Content -Path $logFile -Value "At line: $($_.InvocationInfo.ScriptLineNumber)"
  Add-Content -Path $logFile -Value "Stack Trace:`n$($_.Exception.StackTrace)"
}
finally {
  # Wait for user to hit enter
  Read-Host -Prompt "Press Enter to continue"
}

