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

# Copy only the site‑packages from the builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy your app code
COPY app/ ./app

# Create vector store dir
RUN mkdir -p /app/chroma_db

# Expose & environment variables
ENV PORT=8080 \
    PYTHONPATH=/app \
    VECTOR_STORE_PATH=/app/chroma_db
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Run as non‑root user (optional but recommended)
RUN useradd --create-home appuser
USER appuser

# Start the app with Uvicorn on the correct port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
