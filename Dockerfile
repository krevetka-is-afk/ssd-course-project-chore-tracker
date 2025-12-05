# Build stage
FROM python:3.11-slim AS build
WORKDIR /build

# Install build tools (no strict pinning to avoid Debian mirror mismatches in CI)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer cache
COPY requirements.txt ./

# Install runtime dependencies from requirements file
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --no-deps --prefix=/install --requirement requirements.txt

# Copy project sources (after deps) so changes to source don't bust deps layer
COPY . .

# Runtime stage: minimal, non-root
FROM python:3.11-slim AS runtime

# Set unbuffered output for logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user and a persistent data directory for SQLite
RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /app appuser && \
    mkdir -p /app/data && chown -R appuser:appgroup /app/data /app

# Copy installed packages from build stage into /usr/local
COPY --from=build /install /usr/local

# Copy only application code into final image
COPY --from=build /build .

# Expose port and switch to non-root user
EXPOSE 8000

# Healthcheck uses Python stdlib (no extra utils required)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys,urllib.request as u; u.urlopen('http://127.0.0.1:8000/health').read(); sys.exit(0)" || exit 1

# Switch to non-root user for runtime
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
