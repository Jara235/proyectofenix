@echo off
color 0A
title FENIX 2.0 - Iniciando Servidores...
echo.
echo  ======================================================
echo         SISTEMA FENIX 2.0 - INICIANDO SERVIDORES
echo  ======================================================
echo.

:: Determinar ruta base del proyecto
if exist "%~dp0app_admin.py" (
    set "PROYECTO_DIR=%~dp0"
) else if exist "%~dp0Proyecto fenix\app_admin.py" (
    set "PROYECTO_DIR=%~dp0Proyecto fenix"
) else if exist "%USERPROFILE%\Desktop\Proyecto fenix\app_admin.py" (
    set "PROYECTO_DIR=%USERPROFILE%\Desktop\Proyecto fenix"
) else (
    set "PROYECTO_DIR=C:\Users\JOSE\Desktop\Proyecto fenix"
)

:: Quitar posible diagonal final
if "%PROYECTO_DIR:~-1%"=="\" set "PROYECTO_DIR=%PROYECTO_DIR:~0,-1%"

cd /d "%PROYECTO_DIR%"

:: Detectar ejecutable de Python
set "PYTHON_EXE=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

:: Matar instancias previas si las hay
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 1 /nobreak >nul

echo  Carpeta: %PROYECTO_DIR%
echo.

:: Iniciar 1. Dashboard Principal (Puerto 5000)
echo  [1/3] Iniciando Dashboard Executive (Puerto 5000)...
start "FENIX Dashboard - NO CERRAR" /d "%PROYECTO_DIR%" /min "%PYTHON_EXE%" "dashboard_fenix_v2.py"

:: Iniciar 2. App Captura en Campo (Puerto 5001)
echo  [2/3] Iniciando Captura Campo (Puerto 5001)...
start "FENIX Captura - NO CERRAR" /d "%PROYECTO_DIR%" /min "%PYTHON_EXE%" "app_captura.py"

:: Iniciar 3. App Administracion y Control (Puerto 5002)
echo  [3/3] Iniciando Administracion (Puerto 5002)...
start "FENIX Administracion - NO CERRAR" /d "%PROYECTO_DIR%" /min "%PYTHON_EXE%" "app_admin.py"

echo.
echo  Esperando que arranquen los 3 servidores...
timeout /t 3 /nobreak >nul

:: Abrir el navegador inteligentemente (verifica si ya estan abiertas para no duplicar pestañas)
echo  Verificando pestañas abiertas en el navegador...
"%PYTHON_EXE%" "abrir_navegador.py"

echo.
echo  ======================================================
echo   SISTEMA FENIX 2.0 corriendo en segundo plano.
echo   
echo   1. Dashboard:      http://127.0.0.1:5000
echo   2. Captura Campo:  http://127.0.0.1:5001
echo   3. Administracion: http://127.0.0.1:5002
echo  ======================================================
echo.
timeout /t 5 >nul
exit
