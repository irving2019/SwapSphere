# 🌐 Настройки для домена swapsphere.ru на рег.ру

## 📧 Данные для входа в панель управления рег.ру
- **Логин:** vovapilip46@gmail.com
- **Пароль:** 59Ofavoh
- **Домен:** swapsphere.ru

## 🛠️ Настройка DNS записей в панели управления рег.ру

Зайди в панель управления доменом на https://www.reg.ru и настрой следующие DNS записи:

### A-записи:
```
@ (корень)    A    194.58.112.174
www           A    194.58.112.174
```

### CNAME-записи (опционально):
```
api           CNAME    swapsphere.ru
admin         CNAME    swapsphere.ru
```

### MX-записи для почты (если планируешь использовать почту):
```
@             MX       10 mx1.reg.ru
@             MX       20 mx2.reg.ru
```

## 📧 Настройка почты

Для настройки почты на домене swapsphere.ru:

1. В панели управления рег.ру перейди в раздел "Почта"
2. Создай почтовый ящик: `noreply@swapsphere.ru`
3. Пароль для почты можешь использовать тот же: `59Ofavoh`

### SMTP настройки для Django:
- **Сервер:** smtp.reg.ru
- **Порт:** 587 (TLS) или 465 (SSL)
- **Логин:** noreply@swapsphere.ru
- **Пароль:** 59Ofavoh

## 🔐 SSL сертификат

### Вариант 1: Let's Encrypt (бесплатный)
```bash
sudo certbot --nginx -d swapsphere.ru -d www.swapsphere.ru
```

### Вариант 2: Через панель рег.ру
1. Зайди в панель управления доменом
2. Раздел "SSL сертификаты"
3. Закажи бесплатный Let's Encrypt или купи платный

## 🚀 Быстрое развертывание

1. **Скопируй проект на сервер:**
```bash
git clone https://github.com/irving2019/SwapSphere.git
cd SwapSphere
git checkout Frontend-Fix-Update
```

2. **Настрой переменные окружения:**
```bash
cp .env.production .env
# Файл уже настроен для swapsphere.ru
```

3. **Запусти развертывание:**
```bash
chmod +x deploy_production.sh
./deploy_production.sh
```

4. **Проверь работу:**
- http://swapsphere.ru
- https://swapsphere.ru
- https://swapsphere.ru/admin/

## 📱 Проверочный список

После развертывания проверь:
- [ ] Сайт открывается по адресу swapsphere.ru
- [ ] HTTPS работает (зеленый замочек)
- [ ] www.swapsphere.ru перенаправляется на swapsphere.ru
- [ ] Админка доступна: swapsphere.ru/admin/
- [ ] Статические файлы (CSS/JS) загружаются
- [ ] Загрузка изображений работает
- [ ] Почтовые уведомления отправляются

## 🔧 Команды для управления

```bash
# Просмотр логов
docker compose logs -f

# Перезапуск сервисов
docker compose restart

# Остановка
docker compose down

# Обновление проекта
git pull origin Frontend-Fix-Update
docker compose down
docker compose build
docker compose up -d
```

## 🛡️ Безопасность

- ✅ SECRET_KEY настроен для продакшн
- ✅ DEBUG отключен
- ✅ ALLOWED_HOSTS настроен для swapsphere.ru
- ✅ HTTPS принудительно включен
- ✅ Заголовки безопасности настроены
