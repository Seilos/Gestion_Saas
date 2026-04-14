@echo off
title Nexo21 Core Orchestrator - Servidor de Desarrollo
echo ======================================================
echo INICIANDO ECOSISTEMA NEXO21 (DJANGO + SUPABASE)
echo ======================================================
echo.

:: Verificar si el entorno virtual existe e iniciarlo
if exist venv\Scripts\activate (
    echo [OK] Activando entorno virtual...
    call venv\Scripts\activate
) else (
    echo [!] No se encuentra carpeta 'venv'. Asegurate de tenerla instalada.
)

echo [OK] Servidor corriendo en http://127.0.0.1:8080
echo.
python manage.py runserver 8080
pause
