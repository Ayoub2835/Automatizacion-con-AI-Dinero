FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./

# ---- development: incluye dependencias de test/lint, hot-reload por volumen ----
FROM base AS development
COPY requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- production: imagen mínima, usuario sin privilegios ----
FROM base AS production
RUN pip install -r requirements.txt
COPY . .
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
