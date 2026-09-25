@echo off
TITLE Fenix 2.0 - Guardado y Sincronizacion con GitHub
COLOR 0A

echo ============================================================
echo   SISTEMA FENIX 2.0 - RESPALDO Y SINCRONIZACION CON GITHUB
echo ============================================================
echo.

cd /d "c:\Users\JOSE\Desktop\Proyecto fenix"

echo [1/3] Preparando archivos modificados...
git add .

set CURR_DATE=%date:~10,4%-%date:~4,2%-%date:~7,2%
set CURR_TIME=%time:~0,2%:%time:~3,2%
set COMMIT_MSG=Auto-Sync: Actualizacion de sesion %CURR_DATE% %CURR_TIME%

echo [2/3] Creando commit local con estampa de tiempo...
git commit -m "%COMMIT_MSG%"

echo.
echo [3/3] Subiendo cambios a GitHub (https://github.com/Jara235/proyectofenix.git)...
git push origin main

echo.
echo ============================================================
echo   ✔ PROCESO COMPLETADO: Codigo y documentos subidos a Git
echo ============================================================
echo.
pause
