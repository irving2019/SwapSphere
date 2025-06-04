# PowerShell скрипт для развертывания SwapSphere на Windows Server

Write-Host "🚀 Начинаю развертывание SwapSphere на Windows..." -ForegroundColor Green

# Проверка Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker не установлен! Установите Docker Desktop." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command "docker compose" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose не найден!" -ForegroundColor Red
    exit 1
}

# Создание директорий
Write-Host "📁 Создаю необходимые директории..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "ssl", "logs", "backups" | Out-Null

# Проверка .env файла
if (-not (Test-Path ".env.production")) {
    Write-Host "❌ Файл .env.production не найден!" -ForegroundColor Red
    Write-Host "📝 Скопируйте .env.production и заполните настройки для вашего домена." -ForegroundColor Yellow
    exit 1
}

# Копирование env файла
Copy-Item ".env.production" ".env" -Force
Write-Host "✅ Конфигурация скопирована" -ForegroundColor Green

Write-Host "📦 Сборка Docker образов..." -ForegroundColor Yellow
docker compose -f docker-compose.yml build

Write-Host "🗄️ Запуск базы данных..." -ForegroundColor Yellow
docker compose -f docker-compose.yml up -d db redis

Write-Host "⏳ Ждем готовности базы данных..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "🔄 Выполнение миграций..." -ForegroundColor Yellow
docker compose -f docker-compose.yml run --rm web python manage.py migrate

Write-Host "📊 Создание статических файлов..." -ForegroundColor Yellow
docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput

# Создание суперпользователя
$createAdmin = Read-Host "Хотите создать администратора? (y/n)"
if ($createAdmin -eq "y") {
    Write-Host "👤 Создание суперпользователя..." -ForegroundColor Yellow
    docker compose -f docker-compose.yml run --rm web python manage.py createsuperuser
}

Write-Host "🚀 Запуск всех сервисов..." -ForegroundColor Yellow
docker compose -f docker-compose.yml up -d

Write-Host ""
Write-Host "✅ Развертывание завершено!" -ForegroundColor Green
Write-Host "🌐 Ваш сайт доступен по адресу: http://your-domain.ru" -ForegroundColor Cyan
Write-Host "🔧 Панель администратора: http://your-domain.ru/admin/" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 Полезные команды:" -ForegroundColor Yellow
Write-Host "  Просмотр логов: docker compose logs -f" -ForegroundColor White
Write-Host "  Остановка: docker compose down" -ForegroundColor White
Write-Host "  Перезапуск: docker compose restart" -ForegroundColor White
Write-Host "  Статус: docker compose ps" -ForegroundColor White
