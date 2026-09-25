@echo off
TITLE Fenix 2.0 - Guardado y Sincronizacion con GitHub
COLOR 0A

echo ============================================================
echo   SISTEMA FENIX 2.0 - RESPALDO Y SINCRONIZACION CON GITHUB
echo ============================================================
echo.

cd /d "c:\Users\JOSE\Desktop\Proyecto fenix"

echo [1/3] Guardando y preparando archivos modificados...
git add .

for /f "tokens=*" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"') do set STAMP=%%a
set COMMIT_MSG=Auto-Sync: Respaldo de sesion %STAMP%

echo [2/3] Creando commit local: "%COMMIT_MSG%"...
git commit -m "%COMMIT_MSG%"

echo.
echo [3/3] Subiendo cambios a GitHub (https://github.com/Jara235/proyectofenix.git)...
git push origin main

echo.
echo ============================================================
echo   ✔ PROCESO COMPLETADO: Codigo y documentos subidos a GitHub
echo ============================================================
echo.
pause
