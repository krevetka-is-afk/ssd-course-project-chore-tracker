# Build stage
FROM python:3.11-slim AS build
WORKDIR /build

# Install build tools (no strict pinning to avoid Debian mirror mismatches in CI)
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer cache
COPY requirements.txt ./

# Install runtime dependencies from requirements file (pull transitive deps)
RUN pip install --no-cache-dir --prefix=/install --requirement requirements.txt

# Copy project sources (after deps) so changes to source don't bust deps layer
COPY . .

# Runtime stage: minimal, non-root
FROM python:3.11-slim AS runtime

# Set unbuffered output for logs and disable .pyc writes (read-only root fs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

# Create a non-root user matching docker-compose UID/GID and a writable data dir
ARG APP_UID=1000
ARG APP_GID=1000
RUN addgroup --gid ${APP_GID} appgroup && \
    adduser --disabled-password --gecos '' --uid ${APP_UID} --gid ${APP_GID} --home /app \
      --shell /usr/sbin/nologin appuser && \
    mkdir -p /app/data && chown -R appuser:appgroup /app/data /app

WORKDIR /app

# Copy installed packages from build stage into /usr/local with proper ownership
COPY --from=build --chown=appuser:appgroup /install /usr/local

# Copy only application code into final image
COPY --from=build --chown=appuser:appgroup /build .

# Expose port and switch to non-root user
EXPOSE 8000

# Healthcheck uses Python stdlib (no extra utils required)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys,urllib.request as u; u.urlopen('http://127.0.0.1:8000/health').read(); sys.exit(0)" || exit 1

# Switch to non-root user for runtime
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
