FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base as dependencies

COPY requirements/ /app/requirements/

RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt

FROM dependencies as application

COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Expose port
EXPOSE 8006

# Run gunicorn with configuration file
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
