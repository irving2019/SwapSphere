#!/bin/bash
# Скрипт для развертывания SwapSphere на продакшн сервере

echo "🚀 Начинаю развертывание SwapSphere..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен! Установите Docker и Docker Compose."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    exit 1
fi

# Создание директорий
echo "📁 Создаю необходимые директории..."
mkdir -p ssl
mkdir -p logs
mkdir -p backups

# Проверка .env файла
if [ ! -f .env.production ]; then
    echo "❌ Файл .env.production не найден!"
    echo "📝 Скопируйте .env.production и заполните настройки для вашего домена."
    exit 1
fi

# Копирование env файла
cp .env.production .env

echo "📦 Сборка Docker образов..."
docker compose -f docker-compose.yml build

echo "🗄️ Запуск базы данных..."
docker compose -f docker-compose.yml up -d db redis

echo "⏳ Ждем готовности базы данных..."
sleep 10

echo "🔄 Выполнение миграций..."
docker compose -f docker-compose.yml run --rm web python manage.py migrate

echo "📊 Создание статических файлов..."
docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput

echo "👤 Создание суперпользователя (если нужно)..."
echo "Хотите создать администратора? (y/n)"
read -r create_admin
if [ "$create_admin" = "y" ]; then
    docker compose -f docker-compose.yml run --rm web python manage.py createsuperuser
fi

echo "🚀 Запуск всех сервисов..."
docker compose -f docker-compose.yml up -d

echo "✅ Развертывание завершено!"
echo "🌐 Ваш сайт доступен по адресу: http://your-domain.ru"
echo "🔧 Панель администратора: http://your-domain.ru/admin/"

echo "📋 Полезные команды:"
echo "  Просмотр логов: docker compose logs -f"
echo "  Остановка: docker compose down"
echo "  Перезапуск: docker compose restart"
echo "  Резервная копия БД: docker compose exec db pg_dump -U \$POSTGRES_USER \$POSTGRES_DB > backup.sql"
