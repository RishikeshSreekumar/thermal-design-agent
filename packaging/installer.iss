; Inno Setup script for Thermal Design Agent.
; Build after PyInstaller:  iscc packaging\installer.iss
;
; Installs per-user (no admin rights) into
; %LOCALAPPDATA%\Programs\Thermal Design Agent

#define AppName "Thermal Design Agent"
#define AppVersion "2.0.0"
#define AppExe "ThermalDesignAgent.exe"

[Setup]
AppId={{8D2766AB-1E73-4736-9035-70B401FCC027}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=ThermalDesignAgent-{#AppVersion}-setup
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Files]
Source: "..\dist\ThermalDesignAgent\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
; Default settings: offline mode. Never overwrite a user's existing .env.
Source: "..\packaging\.env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon
Name: "{group}\Edit settings (.env)"; Filename: "notepad.exe"; Parameters: """{app}\.env"""

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Run]
Filename: "notepad.exe"; Parameters: """{app}\.env"""; Description: "Edit settings (Azure OpenAI key) now"; Flags: postinstall nowait skipifsilent unchecked
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: postinstall nowait skipifsilent
