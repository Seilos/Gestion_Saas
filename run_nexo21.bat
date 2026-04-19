@echo off
title Nexo21 Core Orchestrator - Servidor de Desarrollo
echo ======================================================
echo INICIANDO ECOSISTEMA NEXO21 (DJANGO + SUPABASE)
echo ======================================================
echo.

set "VENV_PATH=%~dp0venv"
set "PYTHON_EXE=%VENV_PATH%\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    echo [OK] Entorno virtual detectado.
    echo [INFO] El servidor se abrira en el navegador automaticamente...
    echo.

    :: Lanzar el vigilante en una ventana minimizada separada para no afectar esta consola
    start /min powershell -Command "while(!(Test-NetConnection 127.0.0.1 -Port 8080).TcpTestSucceeded) { Start-Sleep 1 }; start http://127.0.0.1:8080"

    :: Ejecutar Django
    "%PYTHON_EXE%" manage.py runserver 8080
) else (
    echo [ERROR] No se encontro el venv en %VENV_PATH%
)

echo.
echo ======================================================
echo EL SERVIDOR SE HA DETENIDO. LA CONSOLA SE MANTENDRA ABIERTA.
echo ======================================================
:: 'cmd /k' mantiene la consola viva e interactiva pase lo que pase aunque el servidor falle
cmd /k
