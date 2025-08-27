#!/bin/bash
# Salir si hay error
set -o errexit

# Ir al directorio del proyecto (donde está manage.py)
cd $(dirname "$0")

# Ejecutar Gunicorn apuntando al módulo WSGI de Django
gunicorn dondeestudiar.wsgi:application --bind 0.0.0.0:$PORT