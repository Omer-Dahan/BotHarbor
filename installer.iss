; HAMAL Inno Setup Installer Script
; Creates a standard Windows installer from PyInstaller one-folder build

#define MyAppName "HAMAL"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Omer Dahan"
#define MyAppURL "https://github.com/Omer-Dahan/HAMAL"
#define MyAppExeName "HAMAL.exe"

[Setup]
; NOTE: AppId uniquely identifies this application.
; Do not use the same AppId in installers for other applications.
; Double braces required for proper GUID handling.
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Output configuration
OutputDir=installer_output
OutputBaseFilename=HAMAL_Setup_{#MyAppVersion}
; Compression
Compression=lzma2
SolidCompression=yes
; Visual style
WizardStyle=modern
; Admin required for Program Files installation
PrivilegesRequired=admin
; Prevent running installer while app is running
AppMutex=HAMAL_SingleInstance

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Install all files from PyInstaller one-folder build
; Source path is relative to this .iss file location
Source: "dist\HAMAL\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, unchecked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any files created by the app in the install directory
; NOTE: User data in %LOCALAPPDATA%\HAMAL is intentionally NOT deleted
Type: filesandordirs; Name: "{app}"

[Code]
// Show message about user data location on first install
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // User data location reminder (optional)
    // MsgBox('HAMAL stores user data in:' + #13#10 + 
    //        ExpandConstant('{localappdata}\HAMAL'), mbInformation, MB_OK);
  end;
end;
