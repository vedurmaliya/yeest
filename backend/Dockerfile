# ─── Builder Stage ─────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Runtime Stage ─────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages and executables from the builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your app code
COPY app/ ./app

# Create vector store dir with correct permissions
RUN mkdir -p /app/chroma_db && chown -R appuser:appuser /app/chroma_db

# Environment variables & port
ENV PORT=8080 \
    PYTHONPATH=/app \
    VECTOR_STORE_PATH=/app/chroma_db
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Run as non-root user
RUN useradd --create-home appuser
USER appuser

# Start the app (shell form to expand $PORT)
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
