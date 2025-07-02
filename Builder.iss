; Inno Setup Script to install Full Ajax App (Flutter UI + Python Backend)

[Setup]
AppName=Ajax-CRB30
AppVersion=1.0
DefaultDirName={pf}\Ajax-Installer
DefaultGroupName=Ajax-Installer
OutputDir=Ajax-Installer-Build
OutputBaseFilename=Ajax-CRB30
Compression=lzma
SolidCompression=yes

[Files]
; ✅ Include everything in Backend-Builds
Source: "Backend-Builds\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
; ✅ Include everything in Frontend-Builds
Source: "Frontend-Builds\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
; 🎯 Shortcut only for Flutter UI
Name: "{group}\Ajax Dashboard"; Filename: "{app}\iot_dashboard.exe"
Name: "{commondesktop}\Ajax Dashboard"; Filename: "{app}\iot_dashboard.exe"; Tasks: desktopicon

; 🔒 Backend auto-start (runs silently in background)
Name: "{userstartup}\Ajax-Backend"; Filename: "{app}\Ajax-Backend.exe"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
; ▶️ Optionally start backend after install
Filename: "{app}\Ajax-Backend.exe"; Description: "Start background service"; Flags: nowait skipifsilent postinstall

[UninstallDelete]
; 🧹 Remove all EXE files in the install folder during uninstall
Type: files; Name: "{app}\*.exe"
