# Checks version. Returns True if versions match, otherwise False


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



$versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"
$versionsMatch = $false

if (Test-Path $versionFile) {
    $localVersion = Get-Content $versionFile
    try {
        $gitHubVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content
        if ($localVersion -eq $gitHubVersion) {
            $versionsMatch = $true
        }
    } catch {
        Write-Error "Error accessing GitHub version: $_"
    }
}

return $versionsMatch
