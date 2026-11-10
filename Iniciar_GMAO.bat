@echo off
TITLE Servidor GMAO Industrial Pro
COLOR 0B

cd /d "%~dp0"

REM Configurar prioridad de ejecutable Python
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================================
    echo  [AVISO] Python no fue detectado en su equipo o no esta configurado.
    echo  Ejecute Instalar_GMAO_PC.bat para instalar las dependencias requeridas.
    echo ========================================================================
    echo.
    pause
    exit /b 1
)

echo ========================================================================
echo             INICIANDO GMAO INDUSTRIAL PRO (CMMS ENTERPRISE)
echo ========================================================================
echo.

REM Liberar puerto 8000 si un proceso previo colgado lo mantiene ocupado
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

REM Abrir navegador web automaticamente despues de 2 segundos
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8000'"

REM Iniciar el servidor FastAPI / Uvicorn en todas las interfaces de red
%PYTHON_CMD% run.py --host 0.0.0.0 --port 8000

set SERVER_EXIT=%ERRORLEVEL%
if %SERVER_EXIT% EQU 0 goto :fin
if %SERVER_EXIT% EQU 3221225786 goto :fin
if %SERVER_EXIT% EQU -1073741510 goto :fin

echo.
echo [AVISO] El servidor se ha detenido (Codigo: %SERVER_EXIT%).
echo Si hubo algun error de paquetes faltantes, ejecute Instalar_GMAO_PC.bat.
pause

:fin
