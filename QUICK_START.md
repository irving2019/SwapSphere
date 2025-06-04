# 🚀 БЫСТРЫЙ СТАРТ для swapsphere.ru

## 📋 У тебя есть все данные:
- **Домен:** swapsphere.ru  
- **Сервер:** 194.58.112.174
- **Логин рег.ру:** vovapilip46@gmail.com
- **Пароль:** 59Ofavoh

## ⚡ 3 простых шага:

### 1️⃣ Настрой DNS в рег.ру (5 минут)
1. Зайди на https://www.reg.ru
2. Войди: vovapilip46@gmail.com / 59Ofavoh  
3. Найди домен swapsphere.ru → DNS-записи
4. Убедись, что используются DNS-серверы рег.ру:
   - `ns1.reg.ru`
   - `ns2.reg.ru`
5. Добавь A-записи:
   - `@` → `194.58.112.174`
   - `www` → `194.58.112.174`

### 2️⃣ Подключись к серверу
```bash
ssh root@194.58.112.174
```

### 3️⃣ Запусти автоматическое развертывание
```bash
git clone https://github.com/irving2019/SwapSphere.git
cd SwapSphere  
git checkout Frontend-Fix-Update
chmod +x deploy_swapsphere_ru.sh
./deploy_swapsphere_ru.sh
```

## 🎉 Готово!
Через 10-15 минут сайт будет доступен:
- https://swapsphere.ru
- https://swapsphere.ru/admin/

## 🔧 Полезные файлы:
- `DNS_SETUP_GUIDE.md` - подробная настройка DNS
- `check_dns.ps1` - проверка DNS настроек
- `READY_TO_DEPLOY.md` - подробная инструкция
- `REG_RU_SETUP.md` - настройки рег.ру  
- `connect_server.ps1` - быстрое подключение

## 📞 Если что-то не работает:
1. **Проверь DNS:** запусти `.\check_dns.ps1`
2. Проверь DNS онлайн (может занять до 24 часов)
3. Смотри логи: `docker compose logs -f`
4. Перезапуск: `docker compose restart`
