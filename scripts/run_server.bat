@echo off
TITLE GMAO Industrial Pro Server
COLOR 0B
echo ========================================================================
echo                 INICIANDO GMAO INDUSTRIAL PRO (CMMS)
echo ========================================================================
echo.
cd /d "%~dp0\.."

REM Verificar si Python esta en PATH o intentar ruta local
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Python no esta en el PATH global, buscando en instalacion local...
    set PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%
)

powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo Ejecutando servidor con acceso multi-dispositivo en la red...
python run.py --host 0.0.0.0 --port 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar el servidor. Verifique que Python este instalado.
    pause
)
