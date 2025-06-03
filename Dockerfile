# Многоэтапная сборка для оптимизации размера образа
FROM python:3.11-slim as builder

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Основной образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем только необходимые runtime зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаем пользователя для безопасности
RUN addgroup --system app && adduser --system --group app

# Устанавливаем Python зависимости из wheels
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt && \
    rm -rf /wheels requirements.txt

# Создаем рабочую директорию и копируем код
WORKDIR /app
COPY --chown=app:app . .

# Создаем необходимые директории
RUN mkdir -p media/uploads static/collected && \
    chown -R app:app /app

# Переключаемся на непривилегированного пользователя
USER app

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --clear

# Открываем порт
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

# Команда запуска с gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "swapsphere.wsgi:application"]
