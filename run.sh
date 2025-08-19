# exit on error
set -o errexit

# run the web app server
cd $(dirname $(find . | grep manage.py$))
uv run gunicorn $(dirname $(find . | grep wsgi.py$) | sed "s/\.\///g").wsgi:application