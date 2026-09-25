@echo off
color 0B
title FENIX 2.0 - Servidor de Automatización n8n
cls
echo.
echo  ======================================================
echo          SISTEMA FENIX 2.0 - SERVIDOR N8N
echo  ======================================================
echo.
echo   [1/2] Iniciando motor de flujos n8n en puerto 5678...
echo.

:: Configuracion de base de datos PostgreSQL para n8n
set DB_TYPE=postgresdb
set DB_POSTGRESDB_DATABASE=fenix_db
set DB_POSTGRESDB_HOST=localhost
set DB_POSTGRESDB_PORT=5432
set DB_POSTGRESDB_USER=postgres
set DB_POSTGRESDB_PASSWORD=Bupito*268
set DB_POSTGRESDB_SCHEMA=n8n
set N8N_PORT=5678
set N8N_DIAGNOSTICS_ENABLED=false

:: Iniciar n8n con binario global
start "FENIX - Servidor n8n (NO CERRAR)" cmd /k "title n8n Server && n8n start"

echo   [2/2] Esperando que el servidor n8n responda...
timeout /t 6 /nobreak >nul

:: Abrir navegador en n8n
echo.
echo   Abriendo n8n en el navegador: http://localhost:5678
start "" "http://localhost:5678"

echo.
echo  ======================================================
echo   n8n esta corriendo exitosamente en:
echo   URL: http://localhost:5678
echo.
echo   Para detener n8n, cierra la ventana de comando
echo   titulada 'FENIX - Servidor n8n'.
echo  ======================================================
echo.
timeout /t 5 >nul
exit
