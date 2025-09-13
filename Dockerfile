# syntax=docker/dockerfile:1

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_PYTHON_PREFERENCE=only-system \
    UV_PYTHON=/usr/local/bin/python

WORKDIR /app

# System deps (needed for healthcheck + SSL)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (single static binary)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency specs first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a local .venv (from lockfile)
RUN uv sync --frozen --no-dev \
    && uv cache clean

# Ensure venv is preferred on PATH at runtime
ENV PATH="/app/.venv/bin:${PATH}"

# Copy app source
COPY . .

# Expose default port
EXPOSE 5000

# Create volume for downloads directory and make sure it's writeable by non-root
RUN mkdir -p /app/downloads && chmod -R 775 /app/downloads
VOLUME ["/app/downloads"]

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

# Run with uv
CMD ["uv", "run", "main.py"]
