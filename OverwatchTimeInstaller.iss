; Script generated by the Inno Setup Script Wizard.

[Setup]
; General settings
AppName=OverwatchTime
AppVersion=1.0.0
DefaultDirName={pf}\OverwatchTime
DefaultGroupName=OverwatchTime
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=OverwatchTimeInstaller
SetupIconFile=overwatch_time\resources\images\download.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startup"; Description: "Start OverwatchTime on Windows startup"; GroupDescription: "Additional tasks:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\OverwatchTime.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include any other necessary files (e.g., resources)
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu icon
Name: "{group}\OverwatchTime"; Filename: "{app}\OverwatchTime.exe"
; Desktop icon
Name: "{commondesktop}\OverwatchTime"; Filename: "{app}\OverwatchTime.exe"; Tasks: desktopicon

[Run]
; Optionally start the application after installation
Filename: "{app}\OverwatchTime.exe"; Description: "{cm:LaunchProgram,OverwatchTime}"; Flags: nowait postinstall skipifsilent

; Add to startup if selected
Filename: "reg.exe"; Parameters: "ADD HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v OverwatchTime /d ""{app}\OverwatchTime.exe"" /f"; Tasks: startup; Flags: runhidden

[UninstallDelete]
; Remove data files on uninstall (optional)
Type: filesandordirs; Name: "{userappdata}\OverwatchTimeData"
