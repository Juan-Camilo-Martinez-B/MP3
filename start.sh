#!/bin/bash
# Script para iniciar el servidor en Linux/Mac

echo "========================================"
echo " MP3 Player - Iniciando Servidor"
echo "========================================"
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi

# Aplicar migraciones si es necesario
echo "Verificando migraciones..."
python manage.py migrate --noinput

# Iniciar servidor
echo ""
echo "========================================"
echo " Servidor iniciado en:"
echo " http://localhost:8000"
echo "========================================"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver

