# ========================================================================
# GMAO Industrial Pro - Launcher PowerShell para Servidores Windows
# ========================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..")

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "         INICIANDO GMAO INDUSTRIAL PRO (CMMS ENTERPRISE)                " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# Actualizar PATH de sesión si es necesario
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

python run.py --host 0.0.0.0 --port 8000
