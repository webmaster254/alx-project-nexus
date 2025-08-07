# Multi-stage Docker build for Job Board Backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements/development.txt

# Copy project
COPY . .

# Change ownership to app user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=config.settings.development"]

# Production stage
FROM base as production

# Create directories for logs and static files
RUN mkdir -p /var/log/django /var/www/static /var/www/media && \
    chown -R appuser:appuser /var/log/django /var/www/static /var/www/media

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

# Change ownership to app user
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/live/ || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "config.wsgi:application"]