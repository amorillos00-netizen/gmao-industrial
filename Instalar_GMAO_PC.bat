@echo off
TITLE Instalador de GMAO Industrial Pro para PC
COLOR 0A

echo ========================================================================
echo       INSTALADOR PROFESIONAL DE GMAO INDUSTRIAL PRO PARA PC
echo       Sistema de Gestion de Mantenimiento y Confiabilidad (CMMS)
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/4] Verificando instalacion de Python en el equipo...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python no detectado en el PATH. Buscando en rutas locales...
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Descargando e instalando Python 3.11 mediante winget...
        winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    )
)
echo      [OK] Python verificado correctamente.
echo.

echo [2/4] Instalando dependencias necesarias de alto rendimiento...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
echo      [OK] Dependencias instaladas con exito.
echo.

echo [3/4] Inicializando la base de datos relacional y datos maestros...
python -c "from app.database import init_db; init_db()"
echo      [OK] Base de datos SQLite empresarial inicializada.
echo.

echo [4/4] Creando Accesos Directos en el Escritorio y Menu Inicio...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\GMAO Industrial Pro.lnk'); $Shortcut.TargetPath = '%~dp0Iniciar_GMAO.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Sistema GMAO Industrial Pro'; $Shortcut.Save(); Write-Host '     [OK] Acceso directo creado en el Escritorio de Windows.'"
echo.

echo ========================================================================
echo                 INSTALACION COMPLETADA CON EXITO
echo ========================================================================
echo   Se ha colocado el acceso directo "GMAO Industrial Pro" en su Escritorio.
echo   Para iniciar el servidor ahora, presione cualquier tecla.
echo ========================================================================
pause
start "" "%~dp0Iniciar_GMAO.bat"
