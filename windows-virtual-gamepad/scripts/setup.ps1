[CmdletBinding()]
param(
    [ValidateSet('environment','doctor','fetch-driver','install-driver','uninstall-driver')]
    [string]$Action = 'doctor',
    [string]$Python,
    [string]$VenvPath,
    [string]$InstallerPath
)
$ErrorActionPreference = 'Stop'
if (-not $VenvPath) { $VenvPath = Join-Path (Split-Path $PSScriptRoot -Parent) '.venv' }
if ($env:OS -ne 'Windows_NT') { throw 'This skill supports Windows only.' }
$driverUri = 'https://github.com/nefarius/ViGEmBus/releases/download/v1.22.0/ViGEmBus_1.22.0_x64_x86_arm64.exe'
$driverHash = '89220A7865076B342892F98865F3499FB7C4CFD673159E89D352C360FD014C6A'

function Check-Exit([string]$Operation) {
    if ($LASTEXITCODE -ne 0) { throw "$Operation failed (exit $LASTEXITCODE)" }
}
function Check-Driver([string]$Path) {
    $file = Get-Item -LiteralPath $Path
    if ($file.PSIsContainer -or $file.Extension -ne '.exe') { throw 'Expected the official EXE installer.' }
    if ((Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne $driverHash) { throw 'Driver SHA-256 mismatch.' }
    $signature = Get-AuthenticodeSignature -LiteralPath $file.FullName
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Nefarius Software Solutions') {
        throw 'Expected valid Nefarius Authenticode signature.'
    }
    [ordered]@{ sha256=$driverHash; signature=$signature.Status.ToString(); signer=$signature.SignerCertificate.Subject }
}

if ($Action -eq 'doctor') { & (Join-Path $PSScriptRoot 'diagnose.ps1'); exit 0 }
if ($Action -eq 'fetch-driver') {
    if (-not $InstallerPath) { throw 'Pass -InstallerPath for the downloaded EXE.' }
    if (Test-Path -LiteralPath $InstallerPath) { throw 'Destination already exists; inspect it instead of overwriting.' }
    $fullPath = [IO.Path]::GetFullPath($InstallerPath)
    New-Item -ItemType Directory -Path (Split-Path $fullPath -Parent) -Force | Out-Null
    Invoke-WebRequest -Uri $driverUri -OutFile $fullPath -UseBasicParsing
    Check-Driver $fullPath | ConvertTo-Json
    exit 0
}
if ($Action -in @('install-driver','uninstall-driver')) {
    if (-not $InstallerPath) { throw 'Pass -InstallerPath for the official signed installer.' }
    $verified = Check-Driver $InstallerPath
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Driver changes require an elevated PowerShell. Re-run this exact action there; this script does not auto-elevate.'
    }
    $arguments = if ($Action -eq 'install-driver') { '/install /quiet /norestart' } else { '/uninstall /quiet /norestart' }
    $process = Start-Process -FilePath ([IO.Path]::GetFullPath($InstallerPath)) -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -notin @(0,3010,1641)) { throw "Driver operation failed (exit $($process.ExitCode)); inspect Windows installer logs." }
    $verified['action'] = $Action
    $verified['exit_code'] = $process.ExitCode
    $verified['reboot_required'] = ($process.ExitCode -in @(3010,1641))
    $verified | ConvertTo-Json
    exit 0
}

# Environment setup runs unelevated; never lets vgamepad install its bundled driver.
$selectedPython = $null
if ($Python) { $selectedPython = (Get-Command $Python -ErrorAction Stop).Source }
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $selectedPython = (& py -3.12 -E -c 'import sys;print(sys.executable)' 2>$null)
    if ($LASTEXITCODE -ne 0) { $selectedPython = $null }
}
if (-not $selectedPython -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $selectedPython = (Get-Command python).Source
}
if (-not $selectedPython -and (Get-Command uv -ErrorAction SilentlyContinue)) {
    $selectedPython = (& uv python find 3.12 2>$null)
    if ($LASTEXITCODE -ne 0) { $selectedPython = $null }
}
if (-not $selectedPython) { throw 'No suitable Python found. Install Python 3.12, or pass -Python <python.exe>.' }
& $selectedPython -E -c "import sys,platform; assert (3,10)<=sys.version_info[:2]<(3,14); assert platform.machine().lower() in ('amd64','x86_64'); print(sys.version)"
Check-Exit 'Python check (CPython 3.10-3.13 x64 required; 3.12 tested)'
$venvFull = [IO.Path]::GetFullPath($VenvPath)
$venvPython = Join-Path $venvFull 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    if (Test-Path -LiteralPath $venvFull) { throw 'Venv directory exists without Python; use another empty directory.' }
    & $selectedPython -E -m venv $venvFull
    Check-Exit 'venv creation'
}
$previousSkip = $env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL
try {
    $env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL = 'true'
    & $venvPython -E -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
    Check-Exit 'dependency installation'
} finally { $env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL = $previousSkip }
[ordered]@{ python=$venvPython; venv=$venvFull; driver_installed_by_this_action=$false;
    launcher_note='For a custom VenvPath, set VGAMEPAD_PYTHON to the returned Python path.' } | ConvertTo-Json
