@echo off
REM Script para iniciar el servidor en Windows

echo ========================================
echo  MP3 Player - Iniciando Servidor
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Aplicar migraciones si es necesario
echo Verificando migraciones...
py manage.py migrate --noinput

REM Iniciar servidor
echo.
echo ========================================
echo  Servidor iniciado en:
echo  http://localhost:8000
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

py manage.py runserver

pause

