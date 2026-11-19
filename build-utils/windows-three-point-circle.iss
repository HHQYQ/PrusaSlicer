#define Payload GetEnv("PRUSA_INSTALL_PAYLOAD")
#define Output GetEnv("PRUSA_INSTALL_OUTPUT")
#if Payload == "" || Output == ""
  #error PRUSA_INSTALL_PAYLOAD and PRUSA_INSTALL_OUTPUT must be set.
#endif

[Setup]
AppId={{CD88DF34-AB88-423B-870D-4DA3AC903830}
AppName=PrusaSlicer Three-Point Circle
AppVersion=2.9.7.2
AppVerName=PrusaSlicer 2.9.7 Three-Point Circle r2
DefaultDirName={localappdata}\Programs\PrusaSlicer Three-Point Circle
DefaultGroupName=PrusaSlicer Three-Point Circle
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\prusa-slicer.exe
OutputDir={#Output}
OutputBaseFilename=PrusaSlicer-2.9.7-Three-Point-Circle-r2-x64-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#Payload}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PrusaSlicer Three-Point Circle"; Filename: "{app}\prusa-slicer.exe"; WorkingDir: "{app}"
