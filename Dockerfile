# syntax=docker/dockerfile:1

FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional but useful for SSL/ID3, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specs first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy app source
COPY . .

# Expose default port
EXPOSE 5000

# Create volumes: downloads and optional config dir for cookie.txt
VOLUME ["/app/downloads", "/app/config"]

# Healthcheck (basic)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:${PORT:-5000}/health || exit 1

# Default envs (can be overridden at runtime)
ENV HOST=0.0.0.0 \
    PORT=5000 \
    DEBUG=false \
    DOWNLOADS_DIR=downloads \
    LOG_LEVEL=INFO \
    CORS_ORIGINS=* \
    COOKIE_FILE=cookie.txt

# Run the app
CMD ["python", "main.py"]
