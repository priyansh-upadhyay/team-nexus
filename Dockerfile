# ── Frontend Build Stage ──────────────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /web
COPY web/package*.json ./
RUN npm install
COPY web/ .
RUN npm run build:spa

# ── Backend Build Stage ───────────────────────────────────────────────────
FROM python:3.11-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Backend Final Stage ───────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy python packages
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy app code
COPY . .

# Final SPA Hand-off: Find the REAL index.html and move it to static
COPY --from=frontend-builder /web /web-build
RUN mkdir -p /app/static && \
    TARGET_DIR=$(find /web-build/dist -name "index.html" | head -n 1 | xargs dirname) && \
    if [ -n "$TARGET_DIR" ]; then \
        echo "[SUCCESS] Found REAL website files in: $TARGET_DIR"; \
        cp -rv $TARGET_DIR/* /app/static/; \
    else \
        echo "[ERROR] Could not find the built index.html! Build might have failed."; \
        exit 1; \
    fi && \
    rm -rf /web-build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production

RUN chmod +x /app/entrypoint.sh
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
