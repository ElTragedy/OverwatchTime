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

# Program should have 2 use cases.
# First time install and a version update

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
    New-TEm -Path $env:ProgramData\OverwatchTimeData -Name "csvs" -ItemType "directory" -ErrorAction Stop
    Add-Content -Path $logFile -Value "Directory created at $env:ProgramData\OverwatchTimeData\csvs"
  }

  # check if 1. version file exists 2. version in OverwatchTimeData is different
  # from the current version. If so, download the new version from github using wget
  $versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"

  if (Test-Path $versionFile) {
    #compare the version in the file to the current version
    $localVersion = Get-Content .\version.txt
    # wget https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt
    # and whatever is in content is the version
    $gitHubVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content

    if ($localVersion -ne $gitHubVersion) {
      Add-Content -Path $logFile -Value "Local version: $localVersion is different from GitHub version: $gitHubVersion"

      # download the new version from github
      $repoUrl = "https://github.com/ElTragedy/OverwatchTime/archive/refs/heads/main.zip"

      # Define the path where you want to save the ZIP file
      $zipPath = "$env:ProgramData\OverwatchTimeData\OverwatchTime.zip"

      # Create a new WebClient object
      $webClient = New-Object System.Net.WebClient

      # Download the file
      $webClient.DownloadFile($repoUrl, $zipPath)

      # Check for a temp folder, if exists, delete it, then create a new one
      $tempFolder = "$env:ProgramData\OverwatchTimeData\temp"
      if (Test-Path $tempFolder) {
        Remove-Item -Path $tempFolder -Recurse -Force
      }
      # create temp folder
      New-Item -Path $env:ProgramData\OverwatchTimeData -Name "temp" -ItemType "directory" -ErrorAction Stop

      # Define the path where you want to extract the ZIP file
      $extractPath = "$env:ProgramData\OverwatchTimeData\temp"

      # Use Expand-Archive to extract the ZIP file
      Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

      # Remove the ZIP file
      Remove-Item -Path $zipPath -Force

      # We want to replace the following files: version.txt, OverwatchTime.exe,
      # and the images folder
      
      # delete the old version.txt, if it exists
      if(Test-Path $versionFile) {
        Add-Content -Path $logFile -Value "Deleting old version.txt"
        Remove-Item -Path $versionFile -Force
      }

      # move the new verison.txt to the OverwatchTimeData folder
      Move-Item "$extractPath\OverwatchTime-main\version.txt" $versionFile -Force
      Add-Content -Path $logFile -Value "Moved new version.txt to $versionFile"

      # delete the old images folder, if it exists
      if(Test-Path "$env:ProgramData\OverwatchTimeData\images") {
        Remove-Item -Path "$env:ProgramData\OverwatchTimeData\images" -Recurse -Force
      }

      # move images folder
      Move-Item "$extractPath\OverwatchTime-main\images" "$env:ProgramData\OverwatchTimeData" -Force

      # Rename the old exe that is in StartUpFolder\OverwatchTime to OverwatchTime_old.exe
      $oldExe = "$StartUpFolder\OverwatchTime\OverwatchTime.exe"
      Move-Item $oldExe "$StartUpFolder\OverwatchTime\OverwatchTime_old.exe" -Force

      # Move executable to folder we made, overwrite if it already exists

      # Exe should be in StartUpFolder\OverwatchTime

      Copy-Item "$extractPath\OverwatchTime-main\dist\OverwatchTime.exe" "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop

      # terminates, have it check for the old exe and delete it
    }
  }
  else{
    # The user does not have a version file so we will download the latest version
      Add-Content -Path $logFile -Value "Local version does not exist. Downloading the latest version from GitHub."

      # download the new version from github
      $repoUrl = "https://github.com/ElTragedy/OverwatchTime/archive/refs/heads/main.zip"

      # Define the path where you want to save the ZIP file
      $zipPath = "$env:ProgramData\OverwatchTimeData\OverwatchTime.zip"

      # Create a new WebClient object
      $webClient = New-Object System.Net.WebClient

      # Download the file
      $webClient.DownloadFile($repoUrl, $zipPath)

      # Check for a temp folder, if exists, delete it, then create a new one
      $tempFolder = "$env:ProgramData\OverwatchTimeData\temp"
      if (Test-Path $tempFolder) {
        Remove-Item -Path $tempFolder -Recurse -Force
      }
      # create temp folder
      New-Item -Path $env:ProgramData\OverwatchTimeData -Name "temp" -ItemType "directory" -ErrorAction Stop

      # Define the path where you want to extract the ZIP file
      $extractPath = "$env:ProgramData\OverwatchTimeData\temp"

      # Use Expand-Archive to extract the ZIP file
      Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

      # Remove the ZIP file
      Remove-Item -Path $zipPath -Force

      # move the new verison.txt to the OverwatchTimeData folder
      Move-Item "$extractPath\OverwatchTime-main\version.txt" $versionFile -Force

      # move images folder
      Move-Item "$extractPath\OverwatchTime-main\images" "$env:ProgramData\OverwatchTimeData" -Force

      # Move executable to folder we made, overwrite if it already exists
      Copy-Item "$extractPath\OverwatchTime-main\dist\OverwatchTime.exe" "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop
    }

}
catch {
  Add-Content -Path $logFile -Value "An error occurred: $_"
  Add-Content -Path $logFile -Value "At line: $($_.InvocationInfo.ScriptLineNumber)"
  Add-Content -Path $logFile -Value "Stack Trace:`n$($_.Exception.StackTrace)"
}
finally {
  # wait for user to hit enter
  Read-Host -Prompt "Press Enter to continue"
}


