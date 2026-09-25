@echo off
cd /d "%~dp0"
echo =========================================
echo   INICIANDO DASHBOARD FENIX
echo =========================================
echo.
echo El dashboard se abrira automaticamente en tu navegador web.
echo Manten esta ventana negra abierta mientras uses el sistema.
echo.
start http://127.0.0.1:5000
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" dashboard_fenix.py
pause
