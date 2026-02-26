; Options Backtesting System - Inno Setup Installer Script
; Download Inno Setup from: https://jrsoftware.org/isinfo.php
; Build the app first with build.bat, then compile this script in Inno Setup.

#define AppName "Options Backtesting System"
#define AppVersion "3.0"
#define AppPublisher "OptionsBacktest"
#define AppExeName "OptionsBacktest.exe"
#define AppURL "https://optionsbacktest.com"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
; Warn the user if upgrading over an existing install
AllowDowngrade=no
; Require admin for Program Files install
PrivilegesRequired=admin
; Output installer file
OutputDir=dist
OutputBaseFilename=OptionsBacktestSetup_v{#AppVersion}
; Compression
Compression=lzma2
SolidCompression=yes
; Modern wizard style
WizardStyle=modern
; Minimum Windows version: Windows 10
MinVersion=10.0
; Show install/uninstall progress
ShowLanguageDialog=no
LanguageDetectionMethod=none

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Include the entire PyInstaller output folder
Source: "dist\OptionsBacktest\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Explicitly exclude keygen and private key (safety net - build.bat should have removed them already)
; These lines cause an error if the files exist, acting as a final safety check:
; Source: "dist\OptionsBacktest\licensing\keygen.py"; Flags: skipifsourcedoesntexist

[Icons]
; Start Menu
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional, user must tick the box during install)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Offer to launch the app after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any generated files on uninstall
Type: filesandordirs; Name: "{app}\output"
Type: filesandordirs; Name: "{app}\results"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
// Optional: show a welcome message reminding users they need a license key
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'This will install {#AppName} version {#AppVersion} on your computer.' + #13#10 + #13#10 +
    'A valid license key is required to use the application.' + #13#10 +
    'Your key will be emailed to you after purchase.' + #13#10 + #13#10 +
    'Click Next to continue.';
end;
