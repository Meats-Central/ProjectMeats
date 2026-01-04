# FROM python:3.12-slim

# # Set environment variables to prevent writing bytecode and disable buffering
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# WORKDIR /app

# # Install dependencies and clean up to reduce image 
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

# # Copy the Python requirements file and install Python dependencies
# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt \
#     && pip install --no-cache-dir gunicorn whitenoise

# # Copy the application code into the container
# COPY backend/ ./

# # Create directories for staticfiles and media with proper permissions
# RUN mkdir -p /app/staticfiles /app/media

# # Create a non-root user for security and set permissions
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# EXPOSE 8000

# # Healthcheck to ensure the container is running
# HEALTHCHECK --interval=30s --timeout=5s \
#   CMD curl -fsS http://127.0.0.1:8000/api/v1/health/ || exit 1

# # Simple retry mechanism for migrations, ensuring DB is momentarily available
# CMD /bin/sh -c '\
#   for i in 1 2 3 4 5; do \
#     python manage.py migrate --noinput && break || { echo "migrate retry $i"; sleep 3; }; \
#   done && \
#   python manage.py collectstatic --noinput || true && \
#   exec gunicorn projectmeats.wsgi:application \
#     --bind 0.0.0.0:8000 \
#     --workers ${GUNICORN_WORKERS:-3} \
#     --timeout ${GUNICORN_TIMEOUT:-120} \
#     --access-logfile - --error-logfile -'

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn whitenoise

COPY backend/ ./

RUN mkdir -p /app/staticfiles /app/media

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -fsS http://127.0.0.1:8000/api/v1/health/ || exit 1

# Start Gunicorn with debug logging, preload, and error handling
# Use exec form for proper signal handling
# CRITICAL: setup_superuser and collectstatic run on EVERY container start
CMD ["sh", "-c", "set -x && \
    echo \"Starting container at $(date)\" && \
    python manage.py check && \
    echo \"Django check passed\" && \
    echo \"Collecting static files...\" && \
    python manage.py collectstatic --noinput --clear && \
    echo \"Static files collected\" && \
    echo \"Setting up superuser...\" && \
    python manage.py setup_superuser && \
    echo \"Superuser setup complete\" && \
    exec gunicorn projectmeats.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-3} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --preload \
      --log-level debug \
      --capture-output \
      --access-logfile - \
      --error-logfile - || { echo \"Gunicorn failed with exit code $?\"; sleep 300; }"]
