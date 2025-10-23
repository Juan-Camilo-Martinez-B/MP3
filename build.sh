#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Cargar datos iniciales de canciones desde Cloudinary (solo si no existen)
python manage.py load_initial_data

