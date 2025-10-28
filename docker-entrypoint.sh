#!/bin/bash
set -e

echo "Iniciando"

export DJANGO_SETTINGS_MODULE=dondeestudiar.docker_settings

# Generar migraciones automáticamente
python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear

python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser creado: admin/admin123')
else:
    print('ℹSuperuser ya existe')
EOF

echo "Reconstruyendo indice"
python manage.py rebuild_index --noinput || echo "No se pudo reconstruir el indice"

echo "Iniciando servidor Gunicorn en puerto 8000"
exec gunicorn dondeestudiar.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
