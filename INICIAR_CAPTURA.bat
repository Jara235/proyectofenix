@echo off
color 0A
title FENIX 2.0 - Portal de Captura (Puerto 5001)

:: Localizar automaticamente la carpeta del proyecto
if exist "%~dp0app_captura.py" (
    cd /d "%~dp0"
) else if exist "%~dp0Proyecto fenix\app_captura.py" (
    cd /d "%~dp0Proyecto fenix"
) else if exist "%USERPROFILE%\Desktop\Proyecto fenix\app_captura.py" (
    cd /d "%USERPROFILE%\Desktop\Proyecto fenix"
) else (
    cd /d "C:\Users\JOSE\Desktop\Proyecto fenix"
)

echo ======================================================
echo    INICIANDO PORTAL DE CAPTURA FENIX (5001)
echo ======================================================
echo.
echo Carpeta del proyecto: %CD%
echo El modulo se abrira en tu navegador (http://127.0.0.1:5001)
echo.

:: Detectar ejecutable de Python
set "PYTHON_EXE=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

start "" /b "%PYTHON_EXE%" abrir_navegador.py 5001
"%PYTHON_EXE%" app_captura.py
pause

