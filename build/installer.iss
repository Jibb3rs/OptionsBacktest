; Inno Setup script for OptionsBacktest — Windows installer
; Run with: iscc build\installer.iss  (from project root)

#define AppName "OptionsBacktest"
#define AppVersion "4.0.0"
#define AppPublisher "OptionsBacktest"
#define AppExeName "OptionsBacktest.exe"

[Setup]
AppId={{A3F2C1B4-8E7D-4A9F-B6C2-1D3E5F7A9B0C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=https://optionsbacktest.com
AppSupportURL=https://optionsbacktest.com/support
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Output goes to project root dist/ folder
OutputDir=..\dist
OutputBaseFilename=OptionsBacktest-Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; All files from the PyInstaller COLLECT output
Source: "..\dist\OptionsBacktest\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";                         Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}";   Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}";                 Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove any files the app wrote inside its install dir (if any)
Type: filesandordirs; Name: "{app}"
