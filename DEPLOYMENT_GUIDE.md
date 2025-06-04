# 🚀 Инструкция по развертыванию SwapSphere на рег.ру

## 📋 Подготовка

### 1. Требования к серверу
- **VPS/VDS** с Ubuntu 20.04+ или CentOS 8+
- **Минимум 2GB RAM**, 20GB SSD
- **Docker** и **Docker Compose**
- **Nginx** (опционально, если не используете Docker)

### 2. Получение SSL сертификата
У рег.ру можно получить бесплатный SSL сертификат Let's Encrypt или купить платный.

## 🛠️ Установка на VPS/VDS

### Шаг 1: Подключение к серверу
```bash
ssh root@your-server-ip
```

### Шаг 2: Установка Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 3: Загрузка проекта
```bash
# Клонирование репозитория
git clone https://github.com/irving2019/SwapSphere.git
cd SwapSphere
git checkout Frontend-Fix-Update
```

### Шаг 4: Настройка домена
1. **Отредактируй файл `.env.production`:**
```bash
nano .env.production
```

Замени `yourdomain.ru` на свой домен:
```env
ALLOWED_HOSTS=твойдомен.ru,www.твойдомен.ru
EMAIL_HOST_USER=noreply@твойдомен.ru
```

2. **Обнови конфигурацию Nginx:**
```bash
cp nginx_production.conf nginx.conf
nano nginx.conf
```
Замени все `yourdomain.ru` на свой домен.

### Шаг 5: SSL сертификат

#### Вариант A: Let's Encrypt (бесплатный)
```bash
sudo apt install certbot nginx
sudo certbot --nginx -d твойдомен.ru -d www.твойдомен.ru
```

#### Вариант B: Платный SSL от рег.ру
1. Скачай сертификаты от рег.ру
2. Загрузи их на сервер:
```bash
mkdir -p ssl
# Скопируй файлы сертификата в директорию ssl/
```

### Шаг 6: Развертывание
```bash
chmod +x deploy_production.sh
./deploy_production.sh
```

### Шаг 7: Настройка DNS
В панели управления рег.ру добавь A-записи:
- `@` (корень домена) → IP твоего сервера
- `www` → IP твоего сервера

## 🔧 Альтернативный способ (без Docker)

### Если хостинг не поддерживает Docker:

1. **Установи Python и зависимости:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql nginx
```

2. **Создай виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Настрой PostgreSQL:**
```bash
sudo -u postgres createdb swapsphere
sudo -u postgres createuser swapsphere
```

4. **Настрой Gunicorn:**
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 swapsphere.wsgi:application
```

## 📱 Проверка работы

После развертывания проверь:
- ✅ Сайт открывается: `https://твойдомен.ru`
- ✅ HTTPS работает (зеленый замочек)
- ✅ Админка доступна: `https://твойдомен.ru/admin/`
- ✅ Статические файлы загружаются
- ✅ Загрузка изображений работает

## 🔄 Обновление проекта

```bash
cd SwapSphere
git pull origin Frontend-Fix-Update
docker compose down
docker compose build
docker compose up -d
```

## 📞 Поддержка

При возникновении проблем:
1. Проверь логи: `docker compose logs -f`
2. Проверь статус: `docker compose ps`
3. Перезапусти: `docker compose restart`

## 🛡️ Безопасность

- ✅ Смени SECRET_KEY в `.env.production`
- ✅ Используй сильные пароли для БД
- ✅ Настрой firewall (UFW)
- ✅ Регулярно обновляй систему

```bash
# Настройка firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📈 Мониторинг

Для мониторинга работы сайта можешь использовать:
- **UptimeRobot** - бесплатный мониторинг доступности
- **Google Search Console** - для SEO
- **Яндекс.Метрика** - для аналитики
