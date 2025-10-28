#!/bin/bash
set -e

echo "Iniciando"

export DJANGO_SETTINGS_MODULE=dondeestudiar.docker_settings

python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear

echo "Reconstruyendo indice"
python manage.py rebuild_index --noinput || echo "No se pudo reconstruir el indice"

echo "Iniciando servidor Gunicorn en puerto 8000"
exec gunicorn dondeestudiar.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
