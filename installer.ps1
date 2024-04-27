
# Get the current working directory
$CurrentDirectory = (Get-Location).Path
Write-Output "Current directory: $CurrentDirectory"

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

Read-Host -Prompt "Press Enter to continue"


$StartUpFolder = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs"

try {
  # Check if the OverwatchTime directory exists in the start up folder
  if (-not (Test-Path "$StartUpFolder\OverwatchTime")) {
    # Create new folder called OverwatchTime in the start up folder
    New-Item -Path $StartUpFolder -Name "OverwatchTime" -ItemType "directory" -ErrorAction Stop
    Add-Content -Path $logFile -Value "Directory created at $StartUpFolder\OverwatchTime"
  }

  # Move executable to folder we made, overwrite if it already exists
  Copy-Item .\dist\OverwatchTime.exe "$StartUpFolder\OverwatchTime" -Force -ErrorAction Stop
  Add-Content -Path $logFile -Value "Executable copied to $StartUpFolder\OverwatchTime"

  # Check if the OverwatchTimeData directory exists in program data
  if (-not (Test-Path "$env:ProgramData\OverwatchTimeData")) {
    # Create a new folder in program data
    New-Item -Path $env:ProgramData -Name "OverwatchTimeData" -ItemType "directory" -ErrorAction Stop
    Add-Content -Path $logFile -Value "Directory created at $env:ProgramData\OverwatchTimeData"
  }

  # Move everything else into the data folder, overwrite if they already exist
  Move-Item .\* "$env:ProgramData\OverwatchTimeData" -Force -ErrorAction Stop
  Add-Content -Path $logFile -Value "Files moved to $env:ProgramData\OverwatchTimeData"
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


