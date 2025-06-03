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

# Healthcheck (обновлённый)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; response = requests.get('http://localhost:8000/health/', timeout=10); exit(0) if response.status_code == 200 else exit(1)" || exit 1

# Команда запуска с gunicorn (обновлённая с улучшенными настройками производительности)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "--timeout", "120", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "swapsphere.wsgi:application"]
