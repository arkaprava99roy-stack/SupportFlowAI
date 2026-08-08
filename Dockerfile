# Stage 1: Build & Dependencies
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Runtime Image
FROM python:3.12-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root security user
RUN useradd -m -u 10001 appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source code
COPY . .

# Ensure data and logs directories exist and are owned by appuser
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Entrypoint: Run migrations, seed initial data, and launch FastAPI production server
CMD ["sh", "-c", "alembic upgrade head && python -m src.db.seed && uvicorn src.api.app:app --host 0.0.0.0 --port 8000"]
