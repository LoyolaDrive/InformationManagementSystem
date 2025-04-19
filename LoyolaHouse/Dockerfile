FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    netcat-openbsd \
    python3-dev

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media directory
RUN mkdir -p /app/media

# Create a startup script
RUN echo '#!/bin/bash' > /app/start.sh \
    && echo 'echo "Waiting for MySQL database to be ready..."' >> /app/start.sh \
    && echo 'while ! nc -z db 3306; do' >> /app/start.sh \
    && echo '  sleep 0.5' >> /app/start.sh \
    && echo 'done' >> /app/start.sh \
    && echo 'echo "MySQL database is ready!"' >> /app/start.sh \
    && echo 'export DJANGO_SETTINGS_MODULE=LoyolaHouse.docker_settings' >> /app/start.sh \
    && echo 'python manage.py makemigrations' >> /app/start.sh \
    && echo 'python manage.py migrate' >> /app/start.sh \
    && echo 'python manage.py collectstatic --noinput' >> /app/start.sh \
    && echo 'python manage.py runserver 0.0.0.0:8000' >> /app/start.sh \
    && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]
