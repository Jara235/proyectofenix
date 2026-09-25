@echo off
color 0B
title FENIX 2.0 - Administracion y Control (Puerto 5002)

:: Localizar automaticamente la carpeta del proyecto
if exist "%~dp0app_admin.py" (
    cd /d "%~dp0"
) else if exist "%~dp0Proyecto fenix\app_admin.py" (
    cd /d "%~dp0Proyecto fenix"
) else if exist "%USERPROFILE%\Desktop\Proyecto fenix\app_admin.py" (
    cd /d "%USERPROFILE%\Desktop\Proyecto fenix"
) else (
    cd /d "C:\Users\JOSE\Desktop\Proyecto fenix"
)

echo ======================================================
echo    INICIANDO MODULO DE ADMINISTRACION FENIX (5002)
echo ======================================================
echo.
echo Carpeta del proyecto: %CD%
echo El modulo se abrira en tu navegador (http://127.0.0.1:5002)
echo.

:: Detectar ejecutable de Python
set "PYTHON_EXE=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

start "" /b "%PYTHON_EXE%" abrir_navegador.py 5002
"%PYTHON_EXE%" app_admin.py
pause

