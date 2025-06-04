#!/bin/bash
# Скрипт автоматического развертывания SwapSphere на домене swapsphere.ru

echo "🌐 Начинаю развертывание SwapSphere на домене swapsphere.ru..."

# Проверка root прав
if [[ $EUID -eq 0 ]]; then
   echo "❌ Не запускайте скрипт от root! Используйте обычного пользователя с sudo."
   exit 1
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Устанавливаю Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перезайдите в систему и запустите скрипт снова."
    exit 0
fi

if ! command -v docker compose &> /dev/null; then
    echo "📦 Устанавливаю Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создание необходимых директорий
echo "📁 Создаю необходимые директории..."
mkdir -p ssl logs backups

# Настройка Nginx конфигурации для swapsphere.ru
echo "⚙️ Настраиваю Nginx для домена swapsphere.ru..."
cp nginx_production.conf nginx.conf

# Копирование файла окружения
echo "🔧 Настраиваю переменные окружения..."
cp .env.production .env

# Установка Certbot для SSL
echo "🔐 Устанавливаю Certbot для SSL сертификатов..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y certbot nginx-full
elif command -v yum &> /dev/null; then
    sudo yum install -y certbot nginx
fi

# Получение SSL сертификата
echo "🛡️ Получаю SSL сертификат для swapsphere.ru..."
read -p "Хотите автоматически получить SSL сертификат Let's Encrypt? (y/n): " get_ssl
if [ "$get_ssl" = "y" ]; then
    sudo certbot certonly --nginx -d swapsphere.ru -d www.swapsphere.ru --non-interactive --agree-tos --email vovapilip46@gmail.com
    
    # Обновление путей к сертификатам в конфигурации
    sed -i 's|/etc/ssl/certs/swapsphere.ru.crt|/etc/letsencrypt/live/swapsphere.ru/fullchain.pem|g' nginx.conf
    sed -i 's|/etc/ssl/private/swapsphere.ru.key|/etc/letsencrypt/live/swapsphere.ru/privkey.pem|g' nginx.conf
fi

echo "🔨 Сборка Docker образов..."
docker compose -f docker-compose.yml build --no-cache

echo "🗄️ Запуск базы данных и Redis..."
docker compose -f docker-compose.yml up -d db redis

echo "⏳ Ожидание готовности базы данных (30 сек)..."
sleep 30

echo "📊 Выполнение миграций базы данных..."
docker compose -f docker-compose.yml run --rm web python manage.py migrate

echo "📁 Создание статических файлов..."
docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput

echo "👤 Создание суперпользователя..."
read -p "Создать администратора? (y/n): " create_admin
if [ "$create_admin" = "y" ]; then
    docker compose -f docker-compose.yml run --rm web python manage.py createsuperuser
fi

echo "🚀 Запуск всех сервисов..."
docker compose -f docker-compose.yml up -d

# Настройка автоматического обновления SSL
echo "🔄 Настраиваю автоматическое обновление SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Настройка файрвола
echo "🛡️ Настраиваю файрвол..."
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw reload
fi

echo ""
echo "✅ Развертывание SwapSphere завершено!"
echo ""
echo "🌐 Ваш сайт доступен по адресам:"
echo "   • https://swapsphere.ru"
echo "   • https://www.swapsphere.ru (перенаправляется на основной)"
echo ""
echo "🔧 Панель администратора:"
echo "   • https://swapsphere.ru/admin/"
echo ""
echo "📧 Настройки почты:"
echo "   • SMTP: smtp.reg.ru:587"
echo "   • Email: noreply@swapsphere.ru"
echo ""
echo "📋 Полезные команды:"
echo "   • Логи: docker compose logs -f"
echo "   • Статус: docker compose ps"
echo "   • Перезапуск: docker compose restart"
echo "   • Остановка: docker compose down"
echo ""
echo "🔍 Проверьте работу сайта в браузере!"
echo "   Если есть проблемы с DNS, подождите до 24 часов для распространения."
