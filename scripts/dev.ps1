<#
 Panther dev launcher (Windows 11). Checks prerequisites, installs deps, builds the
 sidecar binary Tauri needs at compile time if missing, then runs `tauri dev`.
 The Python sidecar is started and stopped by the Tauri app itself; the legacy
 PySide6 GUI is never launched.
 Usage:  powershell -ExecutionPolicy Bypass -File scripts\dev.ps1
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Need($cmd, $hint) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "Missing prerequisite '$cmd'. $hint"
        exit 1
    }
}
Need python "Install Python 3.10+ from https://www.python.org/downloads/ and tick 'Add to PATH'."
Need node   "Install Node.js 20+ LTS from https://nodejs.org/."
Need cargo  "Install Rust from https://rustup.rs/ (MSVC toolchain; needs Visual Studio Build Tools 'Desktop development with C++')."

$pyOk = python -c "import sys; print(int(sys.version_info >= (3,10)))"
if ($pyOk.Trim() -ne "1") { Write-Error "Python 3.10 or newer is required."; exit 1 }

Write-Host "Installing Python dependencies..."
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed."; exit 1 }

Write-Host "Installing frontend dependencies..."
Push-Location src-tauri\frontend
npm ci
if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "npm ci failed."; exit 1 }
Pop-Location

$bin = "src-tauri\binaries\panther-sidecar-x86_64-pc-windows-msvc.exe"
if (-not (Test-Path $bin)) {
    Write-Host "Building sidecar binary (one-time)..."
    python build_sidecar.py
    if ($LASTEXITCODE -ne 0) { Write-Error "Sidecar build failed."; exit 1 }
}

Write-Host "Starting Panther (Tauri dev)..."
Push-Location src-tauri\frontend
npm run tauri -- dev
$code = $LASTEXITCODE
Pop-Location
exit $code
