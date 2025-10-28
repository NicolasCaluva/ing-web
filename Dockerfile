FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /data

# Asegurar que docker-entrypoint.sh tenga permisos de ejecución
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/docker-entrypoint.sh"]
