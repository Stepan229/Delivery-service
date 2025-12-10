FROM python:3.13-alpine3.21 AS builder
LABEL authors="sskry"

# ARG HTTP_PROXY=http://TKZfRFyA:rDvDMuHV@109.197.16.225:63264
# ARG HTTPS_PROXY=http://TKZfRFyA:rDvDMuHV@109.197.16.225:63264

WORKDIR /app
COPY poetry.lock pyproject.toml .env ./ 

# Установка системных зависимостей для сборки psycopg2
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo

# Установка Poetry и зависимостей
RUN python -m pip install --no-cache-dir poetry==2.2.1 \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

FROM python:3.13-alpine3.21

WORKDIR /app

# Установка РАНТАЙМ зависимостей (без dev-пакетов для сборки)
RUN apk add --no-cache \
    libpq \
    libffi \
    openssl

COPY --from=builder /app /app

# Копируем исходный код
COPY ./src /app

# Устанавливаем путь к Python
ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app