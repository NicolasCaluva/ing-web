# exit on error
set -o errexit

# install project dependencies
uv sync

# entrar al directorio del proyecto (donde está manage.py)
cd $(dirname $(find . | grep manage.py$))

# recopilar estáticos
uv run ./manage.py collectstatic --no-input

# aplicar migraciones
uv run ./manage.py makemigrations
uv run ./manage.py migrate

# crear superusuario solo si definiste la variable de entorno DJANGO_SUPERUSER_PASSWORD
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  uv run ./manage.py createsuperuser \
    --username ${DJANGO_SUPERUSER_USERNAME:-admin} \
    --email ${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"} \
    --noinput || true
fi
