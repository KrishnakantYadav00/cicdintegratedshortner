FROM python:3.12-slim

# Prevent Python from writing bytecode and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Prepare persistent data directory for SQLite volumes
RUN mkdir -p /data && chmod 777 /data
VOLUME ["/data"]

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .
RUN chmod +x docker-entrypoint.sh

# Informational; runtime port is dynamically controlled by $PORT
EXPOSE 5000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '5000'); urllib.request.urlopen(f'http://localhost:{port}/health')" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
