@echo off
cd /d "%~dp0"
echo =========================================
echo   GENERADOR DE REPORTE EXCEL FENIX
echo =========================================
echo.
set /p semana="Ingresa el numero de semana (ej. 26 o 27): "
echo.
echo Generando reporte para Semana %semana%...
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" generar_reporte.py --semana %semana%
echo.
echo Listo! Busca el archivo Reporte_Fenix_Sem%semana%_*.xlsx en esta carpeta.
pause
