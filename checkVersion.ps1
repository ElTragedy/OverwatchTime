# Checks version. Returns True if versions match, otherwise False

# make a boolean and set to false.
$versionsMatch = $false

# check if 1. version file exists 2. version in OverwatchTimeData is different
# from the current version. If so, download the new version from github using wget
$versionFile = "$env:ProgramData\OverwatchTimeData\version.txt"

if (Test-Path $versionFile) {
    #compare the version in the file to the current version
    $localVersion = Get-Content $versionFile 
    # wget https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt
    # and whatever is in content is the version
    $gitHubVersion = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElTragedy/OverwatchTime/main/version.txt" -UseBasicParsing | Select-Object -ExpandProperty Content

    if ($localVersion -eq $gitHubVersion) {
        $versionsMatch = $true
    }
}

return $versionsMatch